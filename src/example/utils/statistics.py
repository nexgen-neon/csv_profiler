import math
from typing import Any

import numpy as np
import pandas as pd


def clean_value(value: Any) -> Any:

    if value is None:
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):

        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, float):

        if math.isnan(value) or math.isinf(value):
            return None

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def percentage(
    part: int | float,
    total: int | float
) -> float:

    if total == 0:
        return 0.0

    return round(
        (part / total) * 100,
        4
    )


def top_values(
    series: pd.Series,
    n: int = 5
) -> list[dict]:

    values = series.dropna()

    counts = values.value_counts().head(n)

    total = len(values)

    result = []

    for value, count in counts.items():

        result.append(
            {
                "value": clean_value(value),
                "count": int(count),
                "percentage": percentage(
                    count,
                    total
                )
            }
        )

    return result