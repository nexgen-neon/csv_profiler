from collections.abc import Iterator

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from example.readers.base_reader import BaseReader


class PostgreSQLReader(BaseReader):
    """
    PostgreSQL reader capable of reading a complete table
    or processing it incrementally in batches.
    """

    DEFAULT_CHUNKSIZE = 100_000

    def __init__(
        self,
        connection_url: str,
        table_name: str,
        schema: str = "public",
        chunksize: int | None = None,
    ):
        self.connection_url = connection_url
        self.table_name = table_name
        self.schema = schema

        self.chunksize = (
            chunksize
            if chunksize is not None
            else self.DEFAULT_CHUNKSIZE
        )

        self.engine: Engine = create_engine(
            self.connection_url
        )

    def read(self) -> pd.DataFrame:
        """
        Read the complete PostgreSQL table.

        Use this for small datasets.
        """

        return pd.read_sql_table(
            table_name=self.table_name,
            con=self.engine,
            schema=self.schema,
        )

    def read_batches(
        self,
        chunksize: int | None = None,
    ) -> Iterator[pd.DataFrame]:
        """
        Read the PostgreSQL table incrementally.

        Each yielded DataFrame contains one batch of rows.
        """

        rows_per_chunk = (
            chunksize
            if chunksize is not None
            else self.chunksize
        )

        reader = pd.read_sql_table(
            table_name=self.table_name,
            con=self.engine,
            schema=self.schema,
            chunksize=rows_per_chunk,
        )

        for dataframe in reader:
            yield dataframe