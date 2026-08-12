import pandas as pd

from example.profiler.categorical_profiler import (
    CategoricalProfiler,
)

from example.profiler.numeric_profiler import (
    NumericalProfiler,
)


class ColumnProfiler:

    IDENTIFIER_KEYWORDS = (
        "id",
        "identifier",
        "key",
        "code",
    )

    def __init__(
        self,
        column_name,
        first_series,
        top_n=5,
    ):

        self.column_name = (
            column_name
        )

        self.dtype = str(
            first_series.dtype
        )

        self.semantic_type = (
            self.detect_semantic_type(
                first_series
            )
        )

        self.total_count = 0
        self.null_count = 0

        self.unique_values = set()

        self.MAX_UNIQUE_TRACKED = 100_000

        self.high_cardinality = False

        self.frequency = {}

        self.top_n = top_n

        self.numerical_profiler = None

        self.categorical_profiler = None

        if self.semantic_type == "numeric":

            self.numerical_profiler = (
                NumericalProfiler()
            )

        elif self.semantic_type == "categorical":

            self.categorical_profiler = (
                CategoricalProfiler(
                    top_n=top_n
                )
            )

    @classmethod
    def detect_semantic_type(
        cls,
        series,
    ):

        dtype = series.dtype

        if pd.api.types.is_bool_dtype(
            dtype
        ):
            return "boolean"

        if pd.api.types.is_datetime64_any_dtype(
            dtype
        ):
            return "datetime"

        if pd.api.types.is_numeric_dtype(
            dtype
        ):

            name = str(
                series.name
            ).lower()

            if any(
                keyword in name
                for keyword
                in cls.IDENTIFIER_KEYWORDS
            ):
                return "identifier"

            return "numeric"

        if pd.api.types.is_object_dtype(
            dtype
        ) or pd.api.types.is_string_dtype(
            dtype
        ):

            name = str(
                series.name
            ).lower()

            if any(
                keyword in name
                for keyword
                in cls.IDENTIFIER_KEYWORDS
            ):

                return "identifier"

            values = (
                series
                .dropna()
                .astype(str)
            )

            if values.empty:
                return "categorical"

            unique_ratio = (
                values.nunique()
                / len(values)
            )

            average_length = (
                values.str.len().mean()
            )

            if (
                unique_ratio > 0.5
                and average_length > 30
            ):

                return "text"

            return "categorical"

        return "categorical"

    def process(self, series):

        self.total_count += len(series)

        self.null_count += int(
            series.isna().sum()
        )

        if self.numerical_profiler:

            self.numerical_profiler.process(
                series
            )

        if self.categorical_profiler:

            self.categorical_profiler.process(
                series
            )

    def finalize(self):

        null_percentage = (
            self.null_count
            / self.total_count
            * 100
            if self.total_count
            else 0.0
        )

        result = {

            "column_name":
                self.column_name,

            "pandas_dtype":
                self.dtype,

            "semantic_type":
                self.semantic_type,

            "null_count":
                self.null_count,

            "null_percentage":
                null_percentage,
        }

        if self.numerical_profiler:

            result[
                "statistics"
            ] = (
                self.numerical_profiler.finalize()
            )

        if self.categorical_profiler:

            result[
                "categorical"
            ] = (
                self.categorical_profiler.finalize()
            )

        return result