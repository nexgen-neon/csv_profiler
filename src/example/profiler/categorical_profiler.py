from collections import Counter


class CategoricalProfiler:

    # Prevent the unique-value set from growing without bounds
    # when profiling very large datasets.
    MAX_UNIQUE_TRACKED = 1000

    def __init__(self, top_n=5):

        self.top_n = top_n

        # Total number of rows processed.
        self.total_count = 0

        # Number of null values.
        self.null_count = 0

        # Number of non-null values.
        self.non_null_count = 0

        # Track unique values.
        self.unique_values = set()

        # Track frequencies of values.
        self.frequency = Counter()

        # Indicates whether the unique-value tracking limit
        # was reached.
        self.high_cardinality = False

    def process(self, series):

        # ---------------------------------------------------------
        # Total values
        # ---------------------------------------------------------

        self.total_count += len(series)

        # ---------------------------------------------------------
        # Null values
        # ---------------------------------------------------------

        null_count = int(
            series.isna().sum()
        )

        self.null_count += null_count

        # ---------------------------------------------------------
        # Non-null values
        # ---------------------------------------------------------

        non_null_count = (
            len(series) - null_count
        )

        self.non_null_count += non_null_count

        # ---------------------------------------------------------
        # Remove null values
        # ---------------------------------------------------------

        values = (
            series
            .dropna()
            .astype(str)
        )

        if values.empty:
            return

        # ---------------------------------------------------------
        # Frequency calculation
        # ---------------------------------------------------------

        counts = values.value_counts()

        for value, count in counts.items():

            self.frequency[value] += int(
                count
            )

        # ---------------------------------------------------------
        # Unique-value tracking
        # ---------------------------------------------------------

        new_values = values.unique()

        remaining = (
            self.MAX_UNIQUE_TRACKED
            - len(self.unique_values)
        )

        if remaining <= 0:

            self.high_cardinality = True

            return

        if len(new_values) > remaining:

            new_values = (
                new_values[:remaining]
            )

            self.high_cardinality = True

        self.unique_values.update(
            new_values.tolist()
        )

    def finalize(self):

        # ---------------------------------------------------------
        # Unique count
        # ---------------------------------------------------------

        unique_count = len(
            self.unique_values
        )

        # ---------------------------------------------------------
        # Unique percentage
        #
        # IMPORTANT:
        #
        # Null values are excluded from the denominator.
        #
        # unique percentage =
        #
        # unique non-null values
        # ----------------------- × 100
        # total non-null values
        # ---------------------------------------------------------

        unique_percentage = (
            unique_count
            / self.non_null_count
            * 100
            if self.non_null_count
            else 0.0
        )

        # ---------------------------------------------------------
        # Most frequent values
        # ---------------------------------------------------------

        top_values = []

        for value, count in (
            self.frequency.most_common(
                self.top_n
            )
        ):

            frequency_percentage = (
                count
                / self.non_null_count
                * 100
                if self.non_null_count
                else 0.0
            )

            top_values.append(
                {
                    "value": value,
                    "frequency": count,
                    "frequency_percentage":
                        frequency_percentage,
                }
            )

        # ---------------------------------------------------------
        # Final result
        # ---------------------------------------------------------

        return {

            "unique_values":
                unique_count,

            "unique_percentage":
                unique_percentage,

            "most_frequent_values":
                top_values,

            "high_cardinality":
                self.high_cardinality,

            "unique_count_note":
                (
                    "Exact while below the "
                    "tracking limit; bounded "
                    "when high-cardinality."
                ),
        }