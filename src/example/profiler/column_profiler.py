import pandas as pd

from .categorical_profiler import CategoricalProfiler
from .numeric_profiler import NumericProfiler


class ColumnProfiler:

    def __init__(
        self,
        column_name: str,
        pandas_dtype: str,
        top_n: int = 5,
    ):

        self.column_name = column_name
        self.pandas_dtype = pandas_dtype

        self.top_n = top_n

        self.total_count = 0
        self.null_count = 0

        self.unique_values = set()

        self.semantic_type = (
            self._detect_semantic_type(
                pandas_dtype
            )
        )

        self.numeric_profiler = None
        self.categorical_profiler = None

        if (
            self.semantic_type
            == "numeric"
        ):

            self.numeric_profiler = (
                NumericProfiler()
            )

        elif (
            self.semantic_type
            == "categorical"
        ):

            self.categorical_profiler = (
                CategoricalProfiler(
                    top_n=top_n
                )
            )

    def process_batch(
        self,
        series: pd.Series,
    ) -> None:

        self.total_count += len(
            series
        )

        self.null_count += int(
            series.isna().sum()
        )

        non_null = series.dropna()

        self.unique_values.update(
            non_null.astype(str).tolist()
        )

        if (
            self.semantic_type
            == "numeric"
        ):

            self.numeric_profiler.process_batch(
                series
            )

        elif (
            self.semantic_type
            == "categorical"
        ):

            self.categorical_profiler.process_batch(
                series
            )

    def finalize(self) -> dict:

        null_percentage = (
            (
                self.null_count
                / self.total_count
            )
            * 100
            if self.total_count
            else 0.0
        )

        unique_count = len(
            self.unique_values
        )

        unique_percentage = (
            (
                unique_count
                / self.total_count
            )
            * 100
            if self.total_count
            else 0.0
        )

        result = {
            "column_name": self.column_name,
            "pandas_dtype": self.pandas_dtype,
            "semantic_type": self.semantic_type,
            "null_count": self.null_count,
            "null_percentage": round(
                null_percentage,
                2,
            ),
            "unique_count": unique_count,
            "unique_percentage": round(
                unique_percentage,
                2,
            ),
        }

        if (
            self.semantic_type
            == "numeric"
        ):

            result[
                "numerical_profile"
            ] = (
                self.numeric_profiler.finalize()
            )

        elif (
            self.semantic_type
            == "categorical"
        ):

            result[
                "categorical_profile"
            ] = (
                self.categorical_profiler.finalize()
            )

        return result

    @staticmethod
    def _detect_semantic_type(
        pandas_dtype: str,
    ) -> str:

        dtype = str(
            pandas_dtype
        ).lower()

        if "bool" in dtype:
            return "boolean"

        if (
            "int" in dtype
            or "float" in dtype
            or "complex" in dtype
        ):
            return "numeric"

        if (
            "datetime" in dtype
            or "date" in dtype
        ):
            return "datetime"

        if (
            "object" in dtype
            or "string" in dtype
            or "category" in dtype
        ):
            return "categorical"

        return "categorical"