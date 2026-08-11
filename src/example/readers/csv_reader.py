from pathlib import Path
from typing import IO, Union

import pandas as pd

from .base_reader import BaseReader


class CSVReader(BaseReader):

    def __init__(
        self,
        source: Union[str, Path, IO[bytes], IO[str]]
    ):
        self.source = source

    def read(self) -> pd.DataFrame:

        try:
            return pd.read_csv(self.source)

        except UnicodeDecodeError:

            if hasattr(self.source, "seek"):
                self.source.seek(0)

            return pd.read_csv(
                self.source,
                encoding="latin1"
            )

        except pd.errors.EmptyDataError as exc:

            raise ValueError(
                "The CSV file is empty."
            ) from exc

        except pd.errors.ParserError as exc:

            raise ValueError(
                f"Invalid CSV input: {exc}"
            ) from exc