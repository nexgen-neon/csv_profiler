import pandas as pd


class DatasetProfiler:

    def __init__(self):

        self.row_count = 0
        self.column_count = 0

        self.memory_usage = 0

        self.duplicate_row_count = 0

        self.empty_row_count = 0

        self.null_count = 0
        self.total_cells = 0

        self.non_null_by_column = {}

        self.seen_row_hashes = set()

    def initialize_columns(
        self,
        columns,
    ):

        self.column_count = len(
            columns
        )

        for column in columns:

            self.non_null_by_column[
                column
            ] = 0

    def process_batch(
        self,
        batch: pd.DataFrame,
    ):

        self.row_count += len(
            batch
        )

        self.total_cells += (
            batch.size
        )

        self.memory_usage += int(
            batch.memory_usage(
                deep=True
            ).sum()
        )

        self.null_count += int(
            batch.isna()
            .sum()
            .sum()
        )

        self.empty_row_count += int(
            batch.isna()
            .all(axis=1)
            .sum()
        )

        non_null_counts = (
            batch.notna().sum()
        )

        for column, count in (
            non_null_counts.items()
        ):

            self.non_null_by_column[
                column
            ] += int(count)

        row_hashes = (
            pd.util.hash_pandas_object(
                batch,
                index=False,
            )
        )

        for row_hash in row_hashes:

            row_hash = int(
                row_hash
            )

            if (
                row_hash
                in self.seen_row_hashes
            ):

                self.duplicate_row_count += 1

            else:

                self.seen_row_hashes.add(
                    row_hash
                )

    def finalize(self):

        completely_empty_columns = [
            column
            for (
                column,
                non_null_count,
            )
            in self.non_null_by_column.items()
            if non_null_count == 0
        ]

        missing_percentage = (
            (
                self.null_count
                / self.total_cells
            )
            * 100
            if self.total_cells
            else 0.0
        )

        return {
            "number_of_rows": self.row_count,
            "number_of_columns": self.column_count,
            "memory_usage_bytes": self.memory_usage,
            "memory_usage_mb": round(
                self.memory_usage
                / (1024 * 1024),
                2,
            ),
            "duplicate_row_count": (
                self.duplicate_row_count
            ),
            "completely_empty_rows": (
                self.empty_row_count
            ),
            "completely_empty_columns": (
                completely_empty_columns
            ),
            "overall_missing_percentage": (
                round(
                    missing_percentage,
                    2,
                )
            ),
        }