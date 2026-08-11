from abc import ABC, abstractmethod

import pandas as pd


class BaseReader(ABC):

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Read data from the source and return
        it as a pandas DataFrame.
        """
        raise NotImplementedError