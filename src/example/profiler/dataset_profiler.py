import pandas as pd
from utils.statistics import percentage

class DatasetProfiler:
    def profile(self, df: pd.DataFrame) -> dict:
        rows,columns = df.shape
        total_cells = rows * columns

        missing_cells = int(
            df.isna().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        if columns > 0:

            empty_rows = int(
                df.isna()
                .all(axis=1)
                .sum()
            )

        else:

            empty_rows = 0

        if rows > 0:

            empty_columns = int(
                df.isna()
                .all(axis=0)
                .sum()
            )

        else:

            empty_columns = columns

        return {

            "rows": int(rows),

            "columns": int(columns),

            "memory_usage_bytes": int(
                df.memory_usage(
                    deep=True
                ).sum()
            ),

            "duplicate_rows":
                duplicate_rows,

            "completely_empty_rows":
                empty_rows,

            "completely_empty_columns":
                empty_columns,

            "missing_values":
                missing_cells,

            "overall_missing_percentage":
                percentage(
                    missing_cells,
                    total_cells
                )
        }