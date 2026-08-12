import pandas as pd

from .column_profiler import ColumnProfiler
from .dataset_profiler import DatasetProfiler


class DataProfiler:

    def __init__(
        self,
        top_n: int = 5,
    ):

        self.top_n = top_n

        self.dataset_profiler = (
            DatasetProfiler()
        )

        self.column_profilers = {}

        self.initialized = False

        self.batch_count = 0

        self.total_input_bytes = 0

    def process_batch(
        self,
        batch: pd.DataFrame,
        batch_size_bytes: int | None = None,
    ):

        if not self.initialized:

            self._initialize(
                batch
            )

        self.batch_count += 1

        if batch_size_bytes is not None:

            self.total_input_bytes += (
                batch_size_bytes
            )

        self.dataset_profiler.process_batch(
            batch
        )

        for column in batch.columns:

            self.column_profilers[
                column
            ].process_batch(
                batch[column]
            )

    def _initialize(
        self,
        batch: pd.DataFrame,
    ):

        columns = list(
            batch.columns
        )

        self.dataset_profiler.initialize_columns(
            columns
        )

        for column in columns:

            self.column_profilers[
                column
            ] = ColumnProfiler(
                column_name=column,
                pandas_dtype=str(
                    batch[column].dtype
                ),
                top_n=self.top_n,
            )

        self.initialized = True

    def finalize(self):

        dataset_profile = (
            self.dataset_profiler.finalize()
        )

        column_profiles = {}

        for (
            column,
            profiler,
        ) in self.column_profilers.items():

            column_profiles[
                column
            ] = profiler.finalize()

        return {
            "dataset_profile": (
                dataset_profile
            ),
            "column_profiles": (
                column_profiles
            ),
            "batch_count": (
                self.batch_count
            ),
            "total_input_bytes": (
                self.total_input_bytes
            ),
            "total_input_mb": round(
                self.total_input_bytes
                / (1024 * 1024),
                2,
            ),
        }