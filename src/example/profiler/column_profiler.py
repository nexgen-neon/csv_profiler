import re
from typing import Any

import pandas as pd

from utils.statistics import (
    clean_value,
    percentage,
    top_values
)

from .numeric_profiler import NumericProfiler
from .categorical_profiler import CategoricalProfiler


class ColumnProfiler:

    # Words that can indicate an identifier column.
    ID_NAME_HINTS = (
        "id",
        "identifier",
        "code",
        "uuid",
        "key",
        "number",
        "no",
        "num"
    )

    def __init__(self):

        self.numeric_profiler = (
            NumericProfiler()
        )

        self.categorical_profiler = (
            CategoricalProfiler()
        )

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    def classify(
        self,
        series: pd.Series
    ) -> str:
        """
        Classify a column into:

        numeric
        categorical
        datetime
        identifier
        text
        boolean
        """

        dtype = series.dtype

        column_name = str(
            series.name
        ).lower()

        non_null = series.dropna()

        # -------------------------------------------------
        # BOOLEAN
        # -------------------------------------------------

        if pd.api.types.is_bool_dtype(dtype):

            return "boolean"

        # -------------------------------------------------
        # DATETIME
        # -------------------------------------------------

        if pd.api.types.is_datetime64_any_dtype(
            dtype
        ):

            return "datetime"

        # -------------------------------------------------
        # NUMERIC
        # -------------------------------------------------

        if pd.api.types.is_numeric_dtype(dtype):

            if len(non_null) == 0:
                return "numeric"

            unique_ratio = (
                non_null.nunique()
                / len(non_null)
            )

            # Check whether column name suggests ID.
            has_id_hint = any(
                re.search(
                    rf"(^|[_\s-])"
                    rf"{re.escape(hint)}"
                    rf"($|[_\s-])",
                    column_name
                )
                for hint in self.ID_NAME_HINTS
            )

            # Numeric column with ID-like name
            # and very high uniqueness.
            if (
                has_id_hint
                and unique_ratio >= 0.90
            ):

                return "identifier"

            return "numeric"

        # -------------------------------------------------
        # STRING / OBJECT
        # -------------------------------------------------

        if (
            pd.api.types.is_object_dtype(dtype)
            or
            pd.api.types.is_string_dtype(dtype)
        ):

            if non_null.empty:

                return "text"

            values = (
                non_null
                .astype(str)
            )

            unique_ratio = (
                values.nunique()
                / len(values)
            )

            # -------------------------------------------------
            # CHECK DATETIME STORED AS STRING
            # -------------------------------------------------

            parsed_dates = pd.to_datetime(
                values,
                errors="coerce"
            )

            if (
                len(values) >= 3
                and
                parsed_dates.notna().mean()
                >= 0.90
            ):

                return "datetime"

            # -------------------------------------------------
            # CHECK IDENTIFIER
            # -------------------------------------------------

            has_id_name = any(
                hint in column_name
                for hint in self.ID_NAME_HINTS
            )

            id_like = (
                has_id_name
                and unique_ratio >= 0.90
            )

            if id_like:

                return "identifier"

            # Very high uniqueness can also indicate
            # an identifier.
            if (
                unique_ratio >= 0.98
                and
                values.str.len().median() <= 40
            ):

                return "identifier"

            # -------------------------------------------------
            # CHECK NUMERIC STORED AS STRING
            # -------------------------------------------------

            numeric_values = pd.to_numeric(
                values,
                errors="coerce"
            )

            if (
                numeric_values.notna().mean()
                >= 0.95
            ):

                return "numeric"

            # -------------------------------------------------
            # CHECK CATEGORICAL
            # -------------------------------------------------

            unique_count = values.nunique()

            if (
                unique_count <= 20
                or
                unique_count
                <= max(
                    20,
                    int(len(values) * 0.05)
                )
            ):

                return "categorical"

            # -------------------------------------------------
            # TEXT
            # -------------------------------------------------

            # Text is classified but not profiled yet.
            return "text"

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        return "text"

    # =====================================================
    # PROFILE COLUMN
    # =====================================================

    def profile(
        self,
        series: pd.Series
    ) -> dict[str, Any]:
        """
        Generate the complete profile for one column.
        """

        rows = len(series)

        # -------------------------------------------------
        # NULL INFORMATION
        # -------------------------------------------------

        null_count = int(
            series.isna().sum()
        )

        non_null = (
            series.dropna()
        )

        # -------------------------------------------------
        # UNIQUE INFORMATION
        # -------------------------------------------------

        unique_count = int(
            non_null.nunique()
        )

        # -------------------------------------------------
        # SEMANTIC TYPE
        # -------------------------------------------------

        semantic_type = (
            self.classify(series)
        )

        # -------------------------------------------------
        # BASIC COLUMN PROFILE
        # -------------------------------------------------

        result = {

            "column_name":
                str(series.name),

            "dtype":
                str(series.dtype),

            "semantic_type":
                semantic_type,

            "null_count":
                null_count,

            "null_percentage":
                percentage(
                    null_count,
                    rows
                ),

            "unique_count":
                unique_count,

            "unique_percentage":
                percentage(
                    unique_count,
                    rows
                ),

            "duplicate_count":
                max(
                    0,
                    len(non_null)
                    - unique_count
                ),

            "constant":
                unique_count <= 1,

            "near_constant":
                False,

            "min":
                None,

            "max":
                None,

            "mean":
                None,

            "median":
                None,

            "std":
                None,

            "variance":
                None,

            "quantiles":
                {},

            "most_frequent_values":
                top_values(
                    series,
                    5
                )
        }

        # -------------------------------------------------
        # EMPTY COLUMN
        # -------------------------------------------------

        if non_null.empty:

            return result

        # -------------------------------------------------
        # NEAR CONSTANT
        # -------------------------------------------------

        frequencies = (
            non_null
            .value_counts(
                normalize=True
            )
        )

        result["near_constant"] = bool(
            frequencies.iloc[0] >= 0.95
        )

        # =================================================
        # NUMERIC
        # =================================================

        if semantic_type == "numeric":

            numeric_stats = (
                self.numeric_profiler
                .profile(series)
            )

            result.update({

                "min":
                    numeric_stats["min"],

                "max":
                    numeric_stats["max"],

                "mean":
                    numeric_stats["mean"],

                "median":
                    numeric_stats["median"],

                "std":
                    numeric_stats["std"],

                "variance":
                    numeric_stats["variance"],

                "quantiles":
                    numeric_stats["percentiles"],

                "numeric_statistics":
                    numeric_stats
            })

        # =================================================
        # IDENTIFIER
        # =================================================

        elif semantic_type == "identifier":

            result[
                "identifier_statistics"
            ] = {

                "unique_values":
                    unique_count,

                "unique_percentage":
                    percentage(
                        unique_count,
                        rows
                    )
            }

        # =================================================
        # CATEGORICAL
        # =================================================

        elif semantic_type == "categorical":

            result[
                "categorical_statistics"
            ] = (
                self.categorical_profiler
                .profile(series)
            )

        # =================================================
        # DATETIME
        # =================================================

        elif semantic_type == "datetime":

            dates = (
                pd.to_datetime(
                    series,
                    errors="coerce"
                )
                .dropna()
            )

            if not dates.empty:

                result["min"] = str(
                    dates.min()
                )

                result["max"] = str(
                    dates.max()
                )

        # =================================================
        # BOOLEAN
        # =================================================

        elif semantic_type == "boolean":

            counts = (
                non_null.value_counts()
            )

            boolean_values = []

            for value, count in (
                counts.head(5).items()
            ):

                boolean_values.append(
                    {
                        "value":
                            clean_value(value),

                        "count":
                            int(count),

                        "percentage":
                            percentage(
                                count,
                                len(non_null)
                            )
                    }
                )

            result[
                "most_frequent_values"
            ] = boolean_values

        # =================================================
        # TEXT
        # =================================================

        elif semantic_type == "text":

            # Text profiling is intentionally not
            # implemented at this stage.
            #
            # The classification remains so that a
            # TextProfiler can be added later.

            result[
                "text_statistics"
            ] = None

        return result