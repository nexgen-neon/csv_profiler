class DatasetProfiler:

    def __init__(self):

        self.total_rows = 0
        self.total_columns = 0

        self.memory_usage_bytes = 0

        self.total_cells = 0
        self.total_missing_values = 0

        self.empty_rows = 0

        self.empty_columns = set()

        self.column_names = []

        self.initialized = False

    def process_batch(self, dataframe):

        if dataframe is None:
            return

        if not self.initialized:

            self.column_names = list(
                dataframe.columns
            )

            self.total_columns = len(
                self.column_names
            )

            self.initialized = True

        if dataframe.empty:
            return

        rows = len(dataframe)

        self.total_rows += rows

        self.total_cells += (
            rows * self.total_columns
        )

        self.memory_usage_bytes += int(
            dataframe.memory_usage(
                index=True,
                deep=True,
            ).sum()
        )

        missing = dataframe.isna()

        self.total_missing_values += int(
            missing.sum().sum()
        )

        self.empty_rows += int(
            missing.all(axis=1).sum()
        )

        empty_columns = (
            dataframe.columns[
                missing.all(axis=0)
            ]
        )

        self.empty_columns.update(
            empty_columns.tolist()
        )

    def finalize(self):

        if self.total_cells:

            missing_percentage = (
                self.total_missing_values
                / self.total_cells
                * 100
            )

        else:

            missing_percentage = 0.0

        return {

            "rows": self.total_rows,

            "columns": self.total_columns,

            "memory_usage_bytes":
                self.memory_usage_bytes,

            "memory_usage_mb":
                self.memory_usage_bytes
                / (1024 ** 2),

            "completely_empty_rows":
                self.empty_rows,

            "completely_empty_columns":
                sorted(
                    self.empty_columns
                ),

            "missing_values":
                self.total_missing_values,

            "overall_missing_percentage":
                missing_percentage,
        }