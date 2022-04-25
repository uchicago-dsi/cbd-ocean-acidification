from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent

class Formatter(ABC):

    @property
    def start(self) -> str:
        """ Name of state to format for """
        return self._state

    @property
    def instructions(self) -> str:
        """ Instructions loaded into README.txt """
        return self._instructions

    def __init__(self):
        """ initialize with proper output directory """
        request_time = datetime.now().strftime("%Y-%m-%dT%H-%M")
        self.relative_path = Path("output") / self.state / request_time
        self.results_directory = HERE.parent / self.relative_path
        self.results_directory.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def format_data_for_agency(self, data: pd.DataFrame) -> Path:
        """ Outermost method for transforming data into agency ready format
        
        Args:
            data: data from collector subclass in standardized format 
        Returns:
            nothing. Creates directory with results.
        """
        return NotImplemented
