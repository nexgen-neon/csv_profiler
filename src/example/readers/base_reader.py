from abc import ABC, abstractmethod
from typing import Iterator

import pandas as pd


class BaseReader(ABC):

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Read the complete dataset.

        Intended primarily for small datasets.
        """
        raise NotImplementedError

    @abstractmethod
    def read_batches(
        self,
        chunksize: int | None = None,
    ) -> Iterator[pd.DataFrame]:
        """
        Read the dataset incrementally.
        """
        raise NotImplementedError