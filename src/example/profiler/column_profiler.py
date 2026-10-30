import re
from datetime import date, datetime, time

import pandas as pd

from example.profiler.categorical_profiler import (
    CategoricalProfiler,
)

from example.profiler.numeric_profiler import (
    NumericalProfiler,
)


class ColumnProfiler:
    VALID_TYPES = {
        "identifier",
        "numeric",
        "categorical",
        "boolean",
        "datetime",
        "time",
        "text",
        "unknown",
    }

    BOOLEAN_VALUES = {
        "true",
        "false",
        "yes",
        "no",
        "y",
        "n",
        "t",
        "f",
        "0",
        "1",
        "0.0",
        "1.0",
    }

    TEXT_BOOLEAN_VALUES = {
        "true",
        "false",
        "yes",
        "no",
        "y",
        "n",
        "t",
        "f",
    }

    # These names describe categories even when stored as numbers.
    CATEGORY_NAMES = {
        "gender",
        "sex",
        "colour",
        "color",
        "learning_style",
        "learningstyle",
        "residence_type",
        "vehicle_type",
        "ms_sub_class",
        "mssubclass",
        "team_jersey_number",
        "nation_jersey_number",
    }

    TEXT_NAMES = {
        "text",
        "description",
        "abstract",
        "excerpt",
        "context",
        "prompt",
        "expected_answer",
        "agent_answer",
        "notes",
        "remarks",
        "definition",
        "definitions",
        "plot",
        "ingredients",
        "firstname",
        "first_name",
        "middlename",
        "middle_name",
        "surname",
        "last_name",
        "short_name",
        "long_name",
    }

    BOOLEAN_NAMES = {
        "real_face",
        "significant",
        "scrabble_valid",
        "is_percent_data",
        "single_parent_household",
        "mental_health_history",
        "late_night_usage",
        "tried_to_cut_back",
        "failed_to_cut_back",
    }

    IDENTIFIER_NAMES = {
        "train_number",
        "vehicle_plate_number",
        "document_number",
        "executive_order_number",
    }

    DATE_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}"
        r"(?:[T ].+)?$"
    )

    TIME_PATTERN = re.compile(
        r"^\d{1,2}:\d{2}"
        r"(?::\d{2}(?:\.\d+)?)?$"
    )

    def __init__(
        self,
        column_name,
        first_series,
        top_n=5,
        semantic_type=None,
    ):
        self.column_name = column_name
        self.dtype = str(first_series.dtype)
        self.top_n = top_n

        self.total_count = 0
        self.null_count = 0

        self.numerical_profiler = None
        self.categorical_profiler = None

        self._forced_type = semantic_type

        if semantic_type is not None:
            if semantic_type not in self.VALID_TYPES:
                raise ValueError(
                    f"Unsupported semantic type: {semantic_type}"
                )

            detected_type = semantic_type

        else:
            detected_type = self.detect_semantic_type(
                first_series,
                column_name=column_name,
            )

        self._configure_type(detected_type)

    @staticmethod
    def normalize_name(column_name):
        name = str(column_name).strip()

        # FastagID -> Fastag_ID
        # userId -> user_Id
        name = re.sub(
            r"([a-z0-9])([A-Z])",
            r"\1_\2",
            name,
        )

        # HTTPCode -> HTTP_Code
        name = re.sub(
            r"([A-Z]+)([A-Z][a-z])",
            r"\1_\2",
            name,
        )

        name = re.sub(
            r"[^a-zA-Z0-9]+",
            "_",
            name,
        )

        return name.strip("_").lower()

    @classmethod
    def is_identifier_name(cls, name):
        tokens = set(name.split("_"))

        if tokens.intersection(
            {"id", "ids", "identifier", "identifiers"}
        ):
            return True

        if name in {
            "userid",
            "movieid",
            "productid",
            "customerid",
            "fastagid",
            "tollboothid",
        }:
            return True

        if name in {
            "primary_key",
            "foreign_key",
        }:
            return True

        return name in cls.IDENTIFIER_NAMES

    @classmethod
    def has_boolean_name(cls, name):
        return (
            name in cls.BOOLEAN_NAMES
            or name.startswith(("is_", "has_"))
            or name.endswith("_flag")
        )

    @staticmethod
    def normalized_values(series):
        return (
            series.dropna()
            .astype(str)
            .str.strip()
            .str.lower()
        )

    @classmethod
    def is_boolean_values(cls, series):
        values = cls.normalized_values(series)

        return (
            not values.empty
            and values.isin(cls.BOOLEAN_VALUES).all()
        )

    @staticmethod
    def parses_as_iso_datetime(value):
        value = str(value).strip()

        # Support UTC suffix in ISO timestamps.
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def parses_as_time(value):
        try:
            time.fromisoformat(str(value).strip())
            return True
        except ValueError:
            return False

    @classmethod
    def detect_semantic_type(
        cls,
        series,
        column_name=None,
    ):
        name = cls.normalize_name(
            column_name
            if column_name is not None
            else series.name
        )

        values = series.dropna()

        # Missing values provide no evidence of semantic meaning.
        if values.empty:
            return "unknown"

        if cls.is_identifier_name(name):
            return "identifier"

        if name in cls.CATEGORY_NAMES:
            return "categorical"

        if pd.api.types.is_bool_dtype(series.dtype):
            return "boolean"

        if pd.api.types.is_datetime64_any_dtype(
            series.dtype
        ):
            return "datetime"

        if name in cls.TEXT_NAMES:
            return "text"

        if name.endswith(("_url", "_path")) or name in {
            "url",
            "path",
        }:
            return "text"

        if (
            cls.has_boolean_name(name)
            and cls.is_boolean_values(values)
        ):
            return "boolean"

        normalized = cls.normalized_values(values)

        # Recognize textual yes/no flags.
        # Plain numeric 0/1 alone is not enough.
        if normalized.isin(cls.TEXT_BOOLEAN_VALUES).all():
            return "boolean"

        if pd.api.types.is_numeric_dtype(series.dtype):
            return "numeric"

        if values.map(
            lambda value: isinstance(value, (date, datetime))
        ).all():
            return "datetime"

        if values.map(
            lambda value: isinstance(value, time)
        ).all():
            return "time"

        strings = values.astype(str).str.strip()

        if (
            strings.str.match(cls.DATE_PATTERN).all()
            and strings.map(cls.parses_as_iso_datetime).all()
        ):
            return "datetime"

        # Only infer clock time for time-like column names.
        # A value such as 4:10 can instead mean a duration.
        if (
            (name == "time" or name.endswith("_time"))
            and strings.str.match(cls.TIME_PATTERN).all()
            and strings.map(cls.parses_as_time).all()
        ):
            return "time"

        numeric_values = pd.to_numeric(
            strings,
            errors="coerce",
        )

        if numeric_values.notna().all():
            # Preserve codes such as 00123 as categories
            # unless an explicit schema says otherwise.
            has_leading_zero = strings.str.match(
                r"^[+-]?0\d+$"
            ).any()

            if has_leading_zero:
                return "categorical"

            return "numeric"

        average_length = strings.str.len().mean()

        average_word_count = (
            strings.str.split()
            .str.len()
            .mean()
        )

        # Repeated paragraphs remain text.
        if (
            average_length >= 80
            or (
                average_length >= 30
                and average_word_count >= 6
            )
        ):
            return "text"

        return "categorical"

    def _configure_type(self, semantic_type):
        self.semantic_type = semantic_type

        self.numerical_profiler = None
        self.categorical_profiler = None

        if semantic_type == "numeric":
            self.numerical_profiler = NumericalProfiler()

        elif semantic_type == "categorical":
            self.categorical_profiler = CategoricalProfiler(
                top_n=self.top_n
            )

    def _validate_and_prepare(self, series):
        values = series.dropna()

        if values.empty:
            return series

        if self.semantic_type == "numeric":
            converted = pd.to_numeric(
                series,
                errors="coerce",
            )

            invalid = series.notna() & converted.isna()

            if invalid.any():
                examples = (
                    series[invalid]
                    .astype(str)
                    .head(3)
                    .tolist()
                )

                raise ValueError(
                    f"Column '{self.column_name}' was classified "
                    f"as numeric but contains non-numeric values: "
                    f"{examples}. Check the source or supply "
                    f"a semantic override."
                )

            return converted

        if self.semantic_type == "boolean":
            if not self.is_boolean_values(values):
                raise ValueError(
                    f"Column '{self.column_name}' was classified "
                    "as boolean but contains other values. "
                    "Check its encoding or semantic override."
                )

        elif self.semantic_type == "datetime":
            if not values.map(
                self.parses_as_iso_datetime
            ).all():
                raise ValueError(
                    f"Column '{self.column_name}' contains "
                    "invalid or unsupported date values. "
                    "Normalize the source date format first."
                )

        elif self.semantic_type == "time":
            if not values.map(
                self.parses_as_time
            ).all():
                raise ValueError(
                    f"Column '{self.column_name}' contains "
                    "invalid or unsupported time values."
                )

        return series

    def process(self, series):
        # A first batch containing only nulls should not
        # permanently determine the column's type.
        if (
            self.semantic_type == "unknown"
            and self._forced_type is None
            and series.notna().any()
        ):
            self.dtype = str(series.dtype)

            self._configure_type(
                self.detect_semantic_type(
                    series,
                    column_name=self.column_name,
                )
            )

            # Earlier all-null batches contributed no values
            # to numerical or categorical statistics.

        prepared = self._validate_and_prepare(series)

        self.total_count += len(series)
        self.null_count += int(series.isna().sum())

        # Nulls are counted above. Subprofilers receive only
        # usable values.
        usable = prepared.dropna()

        if usable.empty:
            return

        if self.numerical_profiler is not None:
            self.numerical_profiler.process(usable)

        if self.categorical_profiler is not None:
            self.categorical_profiler.process(usable)

    def finalize(self):
        null_percentage = (
            self.null_count / self.total_count * 100
            if self.total_count
            else 0.0
        )

        result = {
            "column_name": self.column_name,
            "pandas_dtype": self.dtype,
            "semantic_type": self.semantic_type,
            "null_count": self.null_count,
            "null_percentage": null_percentage,
        }

        if self.numerical_profiler is not None:
            result["statistics"] = (
                self.numerical_profiler.finalize()
            )

        if self.categorical_profiler is not None:
            result["categorical"] = (
                self.categorical_profiler.finalize()
            )

        return result