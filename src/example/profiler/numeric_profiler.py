import heapq
import os
import shutil
import struct
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


class NumericalProfiler:
    """
    Exact numerical profiler designed for both small and huge datasets.

    Features:
        - Exact count
        - Exact null count
        - Exact minimum
        - Exact maximum
        - Exact mean
        - Exact variance
        - Exact standard deviation
        - Exact quantiles
        - Exact median
        - Exact Q1 / Q3
        - Exact IQR
        - Exact IQR-based outlier count

    Large-dataset strategy:
        Numerical values are temporarily stored on disk rather than
        keeping every value in RAM.

    This makes batching and non-batching produce the same statistics.
    """

    # Number of numeric values held in RAM before creating
    # a sorted temporary file.
    SORT_CHUNK_SIZE = 1000

    # Requested percentiles.
    PERCENTILES = [
        1,
        5,
        10,
        25,
        50,
        75,
        90,
        95,
        99,
    ]

    def __init__(self):

        # Basic statistics
        self.count = 0
        self.null_count = 0

        self.minimum = None
        self.maximum = None

        self.sum = 0.0
        self.sum_squared = 0.0

        # Temporary working directory.
        self.temp_dir = Path(
            tempfile.mkdtemp(
                prefix="data_profiler_numeric_"
            )
        )

        # Values waiting to be written to disk.
        self.buffer = []

        # Sorted temporary files.
        self.sorted_files = []

        self.finalized = False

    # =========================================================
    # PROCESS BATCH
    # =========================================================

    def process(self, series):
        """
        Process one pandas Series.

        This method can be called:
            - once with the entire dataset
            - many times with batches

        The final result is identical in both cases.
        """

        if self.finalized:
            raise RuntimeError(
                "NumericalProfiler has already been finalized."
            )

        if series is None:
            return

        # -----------------------------------------------------
        # Count null values
        # -----------------------------------------------------

        self.null_count += int(
            series.isna().sum()
        )

        # -----------------------------------------------------
        # Convert to numeric
        # -----------------------------------------------------

        values = pd.to_numeric(
            series,
            errors="coerce",
        ).dropna()

        if values.empty:
            return

        array = values.to_numpy(
            dtype=np.float64
        )

        # -----------------------------------------------------
        # Basic exact statistics
        # -----------------------------------------------------

        batch_count = len(array)

        self.count += batch_count

        batch_min = float(
            np.min(array)
        )

        batch_max = float(
            np.max(array)
        )

        if self.minimum is None:
            self.minimum = batch_min
        else:
            self.minimum = min(
                self.minimum,
                batch_min,
            )

        if self.maximum is None:
            self.maximum = batch_max
        else:
            self.maximum = max(
                self.maximum,
                batch_max,
            )

        self.sum += float(
            np.sum(array)
        )

        self.sum_squared += float(
            np.sum(array * array)
        )

        # -----------------------------------------------------
        # Store values temporarily
        # -----------------------------------------------------

        self.buffer.extend(
            array.tolist()
        )

        # Once the in-memory buffer reaches the limit,
        # sort it and write it to disk.
        if len(self.buffer) >= self.SORT_CHUNK_SIZE:
            self._flush_buffer()

    # =========================================================
    # FLUSH BUFFER
    # =========================================================

    def _flush_buffer(self):
        """
        Sort the current in-memory values and write them
        to a temporary binary file.

        Only SORT_CHUNK_SIZE values are held in RAM.
        """

        if not self.buffer:
            return

        array = np.asarray(
            self.buffer,
            dtype=np.float64,
        )

        # Sort in RAM.
        array.sort()

        file_path = (
            self.temp_dir
            / f"sorted_{len(self.sorted_files):06d}.bin"
        )

        # Write raw float64 values.
        array.tofile(file_path)

        self.sorted_files.append(
            file_path
        )

        # Release memory.
        self.buffer.clear()

    # =========================================================
    # CREATE SORTED FILES
    # =========================================================

    def _prepare_sorted_files(self):
        """
        Flush any remaining values.
        """

        if self.buffer:
            self._flush_buffer()

    # =========================================================
    # ITERATE SORTED VALUES
    # =========================================================

    def _sorted_values(self):
        """
        Perform an external k-way merge of all sorted
        temporary files.

        Values are yielded in globally sorted order.

        Only a small portion of each file is held in memory.
        """

        if not self.sorted_files:
            return

        file_handles = []

        try:

            # Open all sorted files.
            for file_path in self.sorted_files:

                handle = open(
                    file_path,
                    "rb",
                )

                file_handles.append(handle)

            heap = []

            # Put the first value from every file
            # into the heap.
            for index, handle in enumerate(
                file_handles
            ):

                raw = handle.read(8)

                if raw:

                    value = struct.unpack(
                        "<d",
                        raw,
                    )[0]

                    heapq.heappush(
                        heap,
                        (
                            value,
                            index,
                        ),
                    )

            # K-way merge.
            while heap:

                value, file_index = (
                    heapq.heappop(heap)
                )

                yield value

                handle = file_handles[
                    file_index
                ]

                raw = handle.read(8)

                if raw:

                    next_value = struct.unpack(
                        "<d",
                        raw,
                    )[0]

                    heapq.heappush(
                        heap,
                        (
                            next_value,
                            file_index,
                        ),
                    )

        finally:

            for handle in file_handles:

                try:
                    handle.close()

                except Exception:
                    pass

    # =========================================================
    # GET VALUE AT INDEX
    # =========================================================

    def _value_at_index(self, target_index):
        """
        Return the exact value at a zero-based sorted index.
        """

        if target_index < 0:
            raise IndexError(
                "Index cannot be negative."
            )

        if target_index >= self.count:
            raise IndexError(
                "Index exceeds numeric value count."
            )

        current_index = 0

        for value in self._sorted_values():

            if current_index == target_index:
                return float(value)

            current_index += 1

        raise IndexError(
            "Could not locate requested index."
        )

    # =========================================================
    # EXACT PERCENTILE
    # =========================================================

    def _exact_percentile(self, percentile):
        """
        Calculate percentile using the same linear interpolation
        approach used by numpy.percentile(method='linear').

        This makes the result deterministic and exact.
        """

        if self.count == 0:
            return None

        if self.count == 1:
            return self._value_at_index(0)

        position = (
            (self.count - 1)
            * percentile
            / 100.0
        )

        lower_index = int(
            np.floor(position)
        )

        upper_index = int(
            np.ceil(position)
        )

        if lower_index == upper_index:

            return self._value_at_index(
                lower_index
            )

        lower_value = (
            self._value_at_index(
                lower_index
            )
        )

        upper_value = (
            self._value_at_index(
                upper_index
            )
        )

        fraction = (
            position
            - lower_index
        )

        return float(
            lower_value
            + (
                upper_value
                - lower_value
            )
            * fraction
        )

    # =========================================================
    # EXACT OUTLIER COUNT
    # =========================================================

    def _count_outliers(
        self,
        lower_bound,
        upper_bound,
    ):
        """
        Count outliers across ALL numeric values.

        This is not calculated from a sample.
        """

        count = 0

        for value in self._sorted_values():

            if (
                value < lower_bound
                or value > upper_bound
            ):
                count += 1

        return count

    # =========================================================
    # CLEANUP
    # =========================================================

    def _cleanup(self):
        """
        Remove all temporary files.
        """

        if self.temp_dir.exists():

            shutil.rmtree(
                self.temp_dir,
                ignore_errors=True,
            )

    # =========================================================
    # FINALIZE
    # =========================================================

    def finalize(self):
        """
        Generate the final numerical profile.
        """

        if self.finalized:

            raise RuntimeError(
                "NumericalProfiler.finalize() "
                "has already been called."
            )

        self.finalized = True

        try:

            # -------------------------------------------------
            # No numeric data
            # -------------------------------------------------

            if self.count == 0:

                return {
                    "minimum": None,
                    "maximum": None,
                    "mean": None,
                    "median": None,
                    "standard_deviation": None,
                    "variance": None,
                    "quantiles": {},
                    "q1": None,
                    "q2": None,
                    "q3": None,
                    "iqr": None,
                    "outliers": {
                        "count": 0,
                        "method": "IQR",
                    },
                }

            # -------------------------------------------------
            # Make sure all values are on disk.
            # -------------------------------------------------

            self._prepare_sorted_files()

            # -------------------------------------------------
            # Mean
            # -------------------------------------------------

            mean = (
                self.sum
                / self.count
            )

            # -------------------------------------------------
            # Variance
            # -------------------------------------------------

            variance = max(
                (
                    self.sum_squared
                    / self.count
                )
                - (
                    mean * mean
                ),
                0.0,
            )

            standard_deviation = (
                variance ** 0.5
            )

            # -------------------------------------------------
            # Exact percentiles
            # -------------------------------------------------

            percentile_values = {}

            for percentile in (
                self.PERCENTILES
            ):

                percentile_values[
                    percentile
                ] = self._exact_percentile(
                    percentile
                )

            # -------------------------------------------------
            # Q1 / Median / Q3
            # -------------------------------------------------

            q1 = float(
                percentile_values[25]
            )

            median = float(
                percentile_values[50]
            )

            q3 = float(
                percentile_values[75]
            )

            # -------------------------------------------------
            # IQR
            # -------------------------------------------------

            iqr = float(
                q3 - q1
            )

            # -------------------------------------------------
            # IQR boundaries
            # -------------------------------------------------

            lower_bound = (
                q1
                - 1.5 * iqr
            )

            upper_bound = (
                q3
                + 1.5 * iqr
            )

            # -------------------------------------------------
            # Exact outlier count
            # -------------------------------------------------

            outlier_count = (
                self._count_outliers(
                    lower_bound,
                    upper_bound,
                )
            )

            # -------------------------------------------------
            # Final result
            # -------------------------------------------------

            return {

                "minimum":
                    self.minimum,

                "maximum":
                    self.maximum,

                "mean":
                    mean,

                "median":
                    median,

                "standard_deviation":
                    standard_deviation,

                "variance":
                    variance,

                "quantiles": {

                    "1%":
                        float(
                            percentile_values[1]
                        ),

                    "5%":
                        float(
                            percentile_values[5]
                        ),

                    "10%":
                        float(
                            percentile_values[10]
                        ),

                    "25%":
                        q1,

                    "50%":
                        median,

                    "75%":
                        q3,

                    "90%":
                        float(
                            percentile_values[90]
                        ),

                    "95%":
                        float(
                            percentile_values[95]
                        ),

                    "99%":
                        float(
                            percentile_values[99]
                        ),
                },

                "q1":
                    q1,

                "q2":
                    median,

                "q3":
                    q3,

                "iqr":
                    iqr,

                "outliers": {

                    "count":
                        outlier_count,

                    "method":
                        "IQR",
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                },

                "quantiles_note":
                    (
                        "Exact quantiles calculated "
                        "from all numeric values using "
                        "disk-backed external sorting. "
                        "No reservoir sampling is used."
                    ),
            }

        finally:

            # Always delete temporary files.
            self._cleanup()