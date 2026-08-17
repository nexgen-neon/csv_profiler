from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from example.readers.base_reader import BaseReader


class CSVReader(BaseReader):
    """
    CSV reader capable of processing datasets incrementally.

    The reader does NOT load a huge CSV completely into RAM.
    """

    DEFAULT_CHUNKSIZE = 100_000

    def __init__(
        self,
        source,
        chunksize: int | None = None,
        encoding: str | None = None,
    ):
        self.source = source

        self.chunksize = (
            chunksize
            if chunksize is not None
            else self.DEFAULT_CHUNKSIZE
        )

        self.encoding = encoding

    def read(self) -> pd.DataFrame:
        """
        Read the complete CSV.

        Use this only for small datasets.
        """

        if hasattr(self.source, "seek"):
            self.source.seek(0)

        kwargs = {
            "low_memory": True,
        }

        if self.encoding:
            kwargs["encoding"] = self.encoding

        return pd.read_csv(
            self.source,
            **kwargs,
        )

    def read_batches(
        self,
        chunksize: int | None = None,
    ) -> Iterator[pd.DataFrame]:

        if hasattr(self.source, "seek"):
            self.source.seek(0)

        rows_per_chunk = (
            chunksize
            if chunksize is not None
            else self.chunksize
        )

        kwargs = {
            "chunksize": rows_per_chunk,
            "low_memory": True,
        }

        if self.encoding:
            kwargs["encoding"] = self.encoding

        reader = pd.read_csv(
            self.source,
            **kwargs,
        )

        for dataframe in reader:
            yield dataframe