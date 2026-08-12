import math

import pandas as pd


class NumericProfiler:

    def __init__(self):

        self.count = 0
        self.sum = 0.0

        self.mean = 0.0
        self.m2 = 0.0

        self.minimum = None
        self.maximum = None

        self.values = []

    def process_batch(
        self,
        series: pd.Series,
    ) -> None:

        numeric = pd.to_numeric(
            series,
            errors="coerce",
        ).dropna()

        if numeric.empty:
            return

        values = (
            numeric
            .astype(float)
            .tolist()
        )

        self.values.extend(values)

        batch_min = min(values)
        batch_max = max(values)

        if self.minimum is None:
            self.minimum = batch_min
        else:
            self.minimum = min(
                self.minimum,
                batch_min,
            )

        if self.maximum is None:
            self.maximum = batch_max
        else:
            self.maximum = max(
                self.maximum,
                batch_max,
            )

        for value in values:

            self.count += 1

            delta = (
                value
                - self.mean
            )

            self.mean += (
                delta
                / self.count
            )

            delta2 = (
                value
                - self.mean
            )

            self.m2 += (
                delta
                * delta2
            )

        self.sum += sum(values)

    def finalize(self) -> dict:

        if self.count == 0:

            return {
                "minimum": None,
                "maximum": None,
                "mean": None,
                "median": None,
                "standard_deviation": None,
                "variance": None,
                "quantiles": {},
                "iqr": None,
                "outlier_count": 0,
            }

        variance = (
            self.m2
            / (self.count - 1)
            if self.count > 1
            else 0.0
        )

        standard_deviation = math.sqrt(
            variance
        )

        sorted_values = sorted(
            self.values
        )

        quantiles = {
            "1%": self._quantile(
                sorted_values,
                0.01,
            ),
            "5%": self._quantile(
                sorted_values,
                0.05,
            ),
            "10%": self._quantile(
                sorted_values,
                0.10,
            ),
            "25%": self._quantile(
                sorted_values,
                0.25,
            ),
            "50%": self._quantile(
                sorted_values,
                0.50,
            ),
            "75%": self._quantile(
                sorted_values,
                0.75,
            ),
            "90%": self._quantile(
                sorted_values,
                0.90,
            ),
            "95%": self._quantile(
                sorted_values,
                0.95,
            ),
            "99%": self._quantile(
                sorted_values,
                0.99,
            ),
        }

        q1 = quantiles["25%"]
        q2 = quantiles["50%"]
        q3 = quantiles["75%"]

        iqr = q3 - q1

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        outlier_count = sum(
            1
            for value in self.values
            if (
                value < lower_bound
                or value > upper_bound
            )
        )

        return {
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": round(
                self.mean,
                4,
            ),
            "median": q2,
            "standard_deviation": round(
                standard_deviation,
                4,
            ),
            "variance": round(
                variance,
                4,
            ),
            "quantiles": quantiles,
            "iqr": iqr,
            "outlier_count": outlier_count,
        }

    @staticmethod
    def _quantile(
        sorted_values,
        q,
    ):

        if not sorted_values:
            return 0.0

        position = (
            len(sorted_values) - 1
        ) * q

        lower = int(
            math.floor(position)
        )

        upper = int(
            math.ceil(position)
        )

        if lower == upper:
            return sorted_values[
                lower
            ]

        lower_value = (
            sorted_values[lower]
        )

        upper_value = (
            sorted_values[upper]
        )

        fraction = (
            position - lower
        )

        return (
            lower_value
            + (
                upper_value
                - lower_value
            )
            * fraction
        )