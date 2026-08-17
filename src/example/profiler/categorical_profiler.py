from collections import Counter


class CategoricalProfiler:

    MAX_UNIQUE_TRACKED = 100_000

    def __init__(self, top_n=5):

        self.top_n = top_n

        self.total_count = 0
        self.null_count = 0

        self.unique_values = set()

        self.frequency = Counter()

        self.high_cardinality = False

    def process(self, series):

        self.total_count += len(series)

        self.null_count += int(
            series.isna().sum()
        )

        values = (
            series
            .dropna()
            .astype(str)
        )

        if values.empty:
            return

        # Track frequency.
        counts = values.value_counts()

        for value, count in counts.items():

            self.frequency[value] += int(
                count
            )

        # Track unique values with a hard memory bound.
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

        unique_count = len(
            self.unique_values
        )

        unique_percentage = (
            unique_count
            / self.total_count
            * 100
            if self.total_count
            else 0.0
        )

        non_null_count = (
            self.total_count
            - self.null_count
        )

        top_values = []

        for value, count in (
            self.frequency.most_common(
                self.top_n
            )
        ):

            percentage = (
                count
                / non_null_count
                * 100
                if non_null_count
                else 0.0
            )

            top_values.append(
                {
                    "value": value,
                    "frequency": count,
                    "frequency_percentage":
                        percentage,
                }
            )

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