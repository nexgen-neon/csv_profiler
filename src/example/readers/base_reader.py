from abc import ABC, abstractmethod
from collections.abc import Iterator

import pandas as pd


class BaseReader(ABC):
    """
    Base interface for all data readers.

    Readers must support:
    - normal reading for smaller datasets
    - batch reading for large datasets
    """

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Read the complete dataset."""
        raise NotImplementedError

    @abstractmethod
    def read_batches(
        self,
        batch_size_mb: int = 1000,
    ) -> Iterator[pd.DataFrame]:
        """
        Read the dataset in batches.

        batch_size_mb represents the target raw input
        size of each batch.
        """
        raise NotImplementedError