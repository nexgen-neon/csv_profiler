from example.profiler.column_profiler import (
    ColumnProfiler,
)

from example.profiler.dataset_profiler import (
    DatasetProfiler,
)


class DataProfiler:

    """
    Main orchestration layer.

    It coordinates:
        DatasetProfiler
        ColumnProfiler

    The DataProfiler itself contains NO CSV-specific logic.
    """

    def __init__(
        self,
        top_n=5,
    ):

        self.top_n = top_n

        self.dataset_profiler = (
            DatasetProfiler()
        )

        self.column_profilers = {}

        self.initialized = False

    def _initialize_columns(
        self,
        dataframe,
    ):

        if self.initialized:
            return

        for column in dataframe.columns:

            self.column_profilers[column] = (
                ColumnProfiler(
                    column_name=column,
                    first_series=dataframe[
                        column
                    ],
                    top_n=self.top_n,
                )
            )

        self.initialized = True

    def process_batch(
        self,
        dataframe,
    ):

        if dataframe is None:
            return

        if dataframe.empty:
            return

        # Dataset-level profiling
        self.dataset_profiler.process_batch(
            dataframe
        )

        # Initialize column profilers
        self._initialize_columns(
            dataframe
        )

        # Column-level profiling
        for column in dataframe.columns:

            self.column_profilers[
                column
            ].process(
                dataframe[column]
            )

    def generate(self):

        columns = {}

        for column_name, profiler in (
            self.column_profilers.items()
        ):

            columns[column_name] = (
                profiler.finalize()
            )

        return {

            "dataset":
                self.dataset_profiler.finalize(),

            "columns":
                columns,
        }