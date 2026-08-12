from collections import Counter

import pandas as pd


class CategoricalProfiler:
    """
    Streaming categorical profiler.

    Calculates:

    - Unique values
    - Unique percentage
    - Most frequent values
    - Frequency
    - Frequency percentage
    """

    def __init__(self, top_n: int = 5):
        self.top_n = top_n

        self.value_counts = Counter()

        self.total_count = 0
        self.non_null_count = 0

    def process_batch(
        self,
        series: pd.Series,
    ) -> None:

        self.total_count += len(series)

        non_null = series.dropna()

        self.non_null_count += len(
            non_null
        )

        counts = Counter(
            non_null.astype(str).tolist()
        )

        self.value_counts.update(
            counts
        )

    def finalize(self) -> dict:

        unique_values = len(
            self.value_counts
        )

        unique_percentage = (
            (
                unique_values
                / self.non_null_count
            )
            * 100
            if self.non_null_count
            else 0.0
        )

        top_values = (
            self.value_counts
            .most_common(self.top_n)
        )

        most_frequent_values = []

        for value, frequency in top_values:

            frequency_percentage = (
                (
                    frequency
                    / self.non_null_count
                )
                * 100
                if self.non_null_count
                else 0.0
            )

            most_frequent_values.append(
                {
                    "value": value,
                    "frequency": frequency,
                    "frequency_percentage": round(
                        frequency_percentage,
                        2,
                    ),
                }
            )

        return {
            "unique_values": unique_values,
            "unique_percentage": round(
                unique_percentage,
                2,
            ),
            "most_frequent_values": (
                most_frequent_values
            ),
        }