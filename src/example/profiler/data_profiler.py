import pandas as pd

from .dataset_profiler import DatasetProfiler
from .column_profiler import ColumnProfiler


class DataProfiler:

    def __init__(
        self,
        data: pd.DataFrame,
        dataset_name: str = "dataset"
    ):
        """
        Initialize the profiler.

        DataProfiler receives a pandas DataFrame.
        It does NOT care whether the DataFrame came
        from CSV, JSON, database, Parquet, etc.
        """

        if not isinstance(
            data,
            pd.DataFrame
        ):

            raise TypeError(
                "DataProfiler expects "
                "a pandas DataFrame."
            )

        self.data = data

        self.dataset_name = (
            dataset_name
        )

        self.dataset_profiler = (
            DatasetProfiler()
        )

        self.column_profiler = (
            ColumnProfiler()
        )

    # =====================================================
    # GENERATE COMPLETE PROFILE
    # =====================================================

    def generate(self) -> dict:
        """
        Generate the complete profile.
        """

        # -------------------------------------------------
        # DATASET LEVEL
        # -------------------------------------------------

        dataset_statistics = (
            self.dataset_profiler
            .profile(self.data)
        )

        # -------------------------------------------------
        # COLUMN LEVEL
        # -------------------------------------------------

        column_statistics = {}

        for column in self.data.columns:

            column_statistics[
                str(column)
            ] = self.column_profiler.profile(
                self.data[column]
            )

        # -------------------------------------------------
        # FINAL PROFILE
        # -------------------------------------------------

        return {

            "dataset": {

                "name":
                    self.dataset_name,

                **dataset_statistics
            },

            "columns":
                column_statistics
        }