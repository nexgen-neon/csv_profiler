import random

import numpy as np
import pandas as pd


class NumericalProfiler:

    RESERVOIR_SIZE = 100_000

    def __init__(self):

        self.count = 0

        self.null_count = 0

        self.minimum = None
        self.maximum = None

        self.sum = 0.0
        self.sum_squared = 0.0

        self.reservoir = []

    def process(self, series):

        self.null_count += int(
            series.isna().sum()
        )

        values = pd.to_numeric(
            series,
            errors="coerce",
        ).dropna()

        if values.empty:
            return

        array = values.to_numpy(
            dtype=float
        )

        batch_count = len(array)

        self.count += batch_count

        batch_min = float(
            np.min(array)
        )

        batch_max = float(
            np.max(array)
        )

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

        self.sum += float(
            np.sum(array)
        )

        self.sum_squared += float(
            np.sum(
                array * array
            )
        )

        self._update_reservoir(
            array
        )

    def _update_reservoir(self, array):

        for value in array:

            if len(self.reservoir) < self.RESERVOIR_SIZE:

                self.reservoir.append(
                    float(value)
                )

                continue

            position = random.randint(
                0,
                self.count - 1,
            )

            if position < self.RESERVOIR_SIZE:

                self.reservoir[position] = (
                    float(value)
                )

    def finalize(self):

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
                "outliers": {
                    "count": 0,
                    "method": "IQR",
                },
            }

        mean = (
            self.sum
            / self.count
        )

        variance = max(
            (
                self.sum_squared
                / self.count
            )
            - (mean * mean),
            0.0,
        )

        std = variance ** 0.5

        sample = np.asarray(
            self.reservoir,
            dtype=float,
        )

        percentiles = np.percentile(
            sample,
            [
                1,
                5,
                10,
                25,
                50,
                75,
                90,
                95,
                99,
            ],
        )

        q1 = float(percentiles[3])
        q2 = float(percentiles[4])
        q3 = float(percentiles[5])

        iqr = q3 - q1

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        outlier_count = int(
            np.sum(
                (sample < lower_bound)
                |
                (sample > upper_bound)
            )
        )

        return {

            "minimum":
                self.minimum,

            "maximum":
                self.maximum,

            "mean":
                mean,

            "median":
                q2,

            "standard_deviation":
                std,

            "variance":
                variance,

            "quantiles": {

                "1%":
                    float(percentiles[0]),

                "5%":
                    float(percentiles[1]),

                "10%":
                    float(percentiles[2]),

                "25%":
                    q1,

                "50%":
                    q2,

                "75%":
                    q3,

                "90%":
                    float(percentiles[6]),

                "95%":
                    float(percentiles[7]),

                "99%":
                    float(percentiles[8]),
            },

            "q1": q1,

            "q2": q2,

            "q3": q3,

            "iqr": iqr,

            "outliers": {

                "count":
                    outlier_count,

                "method":
                    "IQR",
            },

            "quantiles_note":
                "Quantiles and IQR outliers "
                "are estimated from a bounded "
                "reservoir sample.",
        }