import numpy as np
import pandas as pd

from utils.statistics import (
    clean_value,
    percentage
)


class NumericProfiler:

    PERCENTILES = [
        1,
        5,
        10,
        25,
        50,
        75,
        90,
        95,
        99
    ]

    def profile(
        self,
        series: pd.Series
    ) -> dict:

        numeric = pd.to_numeric(
            series,
            errors="coerce"
        ).dropna()

        if numeric.empty:

            return {

                "min": None,

                "max": None,

                "mean": None,

                "median": None,

                "std": None,

                "variance": None,

                "percentiles": {
                    str(p): None
                    for p in self.PERCENTILES
                },

                "q1": None,

                "q2": None,

                "q3": None,

                "iqr": None,

                "outliers": {
                    "count": 0,
                    "percentage": 0.0,
                    "method": "IQR"
                }
            }

        q1 = numeric.quantile(0.25)

        q2 = numeric.quantile(0.50)

        q3 = numeric.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - (
            1.5 * iqr
        )

        upper_bound = q3 + (
            1.5 * iqr
        )

        outliers = numeric[
            (numeric < lower_bound)
            |
            (numeric > upper_bound)
        ]

        return {

            "min":
                clean_value(
                    numeric.min()
                ),

            "max":
                clean_value(
                    numeric.max()
                ),

            "mean":
                clean_value(
                    numeric.mean()
                ),

            "median":
                clean_value(
                    numeric.median()
                ),

            "std":
                clean_value(
                    numeric.std()
                ),

            "variance":
                clean_value(
                    numeric.var()
                ),

            "percentiles": {

                str(p):
                    clean_value(
                        np.percentile(
                            numeric,
                            p
                        )
                    )

                for p in self.PERCENTILES
            },

            "q1":
                clean_value(q1),

            "q2":
                clean_value(q2),

            "q3":
                clean_value(q3),

            "iqr":
                clean_value(iqr),

            "outliers": {

                "count":
                    int(len(outliers)),

                "percentage":
                    percentage(
                        len(outliers),
                        len(numeric)
                    ),

                "method":
                    "IQR",

                "lower_bound":
                    clean_value(
                        lower_bound
                    ),

                "upper_bound":
                    clean_value(
                        upper_bound
                    )
            }
        }