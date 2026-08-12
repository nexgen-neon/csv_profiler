import io
from collections.abc import Iterator

import pandas as pd

from .base_reader import BaseReader


class CSVReader(BaseReader):
    """
    CSV reader supporting fixed-size byte/MB batches.

    Large datasets are processed approximately 1000 MB
    of raw CSV data at a time.
    """

    DEFAULT_BATCH_SIZE_MB = 1000

    def __init__(self, file):
        self.file = file

    def read(self) -> pd.DataFrame:
        """
        Read the complete CSV.

        This should only be used for smaller datasets.
        """

        if hasattr(self.file, "seek"):
            self.file.seek(0)

        return pd.read_csv(self.file)

    def read_batches(
        self,
        batch_size_mb: int = DEFAULT_BATCH_SIZE_MB,
    ) -> Iterator[pd.DataFrame]:
        """
        Read CSV in approximately fixed-size MB batches.

        Each complete batch targets exactly the configured
        batch size. The final batch may be smaller.
        """

        if batch_size_mb != self.DEFAULT_BATCH_SIZE_MB:
            raise ValueError(
                "Large-dataset batch size must be exactly "
                "1000 MB."
            )

        batch_size_bytes = (
            batch_size_mb * 1024 * 1024
        )

        # --------------------------------------------------
        # Open the source
        # --------------------------------------------------

        should_close = False

        if isinstance(self.file, (str, bytes)):
            file_object = open(
                self.file,
                "rb",
            )
            should_close = True

        else:
            file_object = self.file

        try:
            if hasattr(file_object, "seek"):
                file_object.seek(0)

            # --------------------------------------------------
            # Read header
            # --------------------------------------------------

            header = file_object.readline()

            if not header:
                return

            header_text = header.decode(
                "utf-8",
                errors="replace",
            )

            # --------------------------------------------------
            # Build batches
            # --------------------------------------------------

            batch_lines = []
            current_batch_size = 0

            while True:

                line = file_object.readline()

                if not line:
                    break

                line_size = len(line)

                # --------------------------------------------------
                # If adding this line would exceed 1000 MB,
                # process the current batch first.
                # --------------------------------------------------

                if (
                    batch_lines
                    and
                    current_batch_size + line_size
                    > batch_size_bytes
                ):

                    batch_data = (
                        header
                        + b"".join(batch_lines)
                    )

                    batch = pd.read_csv(
                        io.BytesIO(batch_data)
                    )

                    yield batch

                    batch_lines = []
                    current_batch_size = 0

                batch_lines.append(line)
                current_batch_size += line_size

            # --------------------------------------------------
            # Final batch
            # --------------------------------------------------

            if batch_lines:

                batch_data = (
                    header
                    + b"".join(batch_lines)
                )

                batch = pd.read_csv(
                    io.BytesIO(batch_data)
                )

                yield batch

        finally:

            if should_close:
                file_object.close()