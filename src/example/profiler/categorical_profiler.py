import pandas as pd

from utils.statistics import percentage


class CategoricalProfiler:

    def profile(self, series: pd.Series) -> dict:
        """
        Profile a categorical column.

        Calculates:
        - Unique values
        - Unique percentage
        - Most frequent values
        - Frequency of each top value
        - Frequency percentage
        """

        # Remove null values because frequency
        # analysis is performed on actual values.
        non_null = series.dropna()

        # Total number of non-null values
        total_values = len(non_null)

        # -------------------------------------------------
        # UNIQUE VALUES
        # -------------------------------------------------

        unique_values = int(
            non_null.nunique()
        )

        # -------------------------------------------------
        # UNIQUE PERCENTAGE
        # -------------------------------------------------

        unique_percentage = percentage(
            unique_values,
            len(series)
        )

        # -------------------------------------------------
        # FREQUENCY OF EACH VALUE
        # -------------------------------------------------

        value_counts = (
            non_null.value_counts()
        )

        # -------------------------------------------------
        # TOP 5 MOST FREQUENT VALUES
        # -------------------------------------------------

        most_frequent_values = []

        for value, frequency in (
            value_counts.head(5).items()
        ):

            frequency = int(frequency)

            frequency_percentage = percentage(
                frequency,
                total_values
            )

            most_frequent_values.append(
                {
                    "value": str(value),

                    "frequency":
                        frequency,

                    "frequency_percentage":
                        frequency_percentage
                }
            )

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return {

            "unique_values":
                unique_values,

            "unique_percentage":
                unique_percentage,

            "most_frequent_values":
                most_frequent_values
        }