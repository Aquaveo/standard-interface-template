"""Simulation data class."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules
from xmscomponents.bases.xarray_base import XarrayBase

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationData(XarrayBase):
    """Manages data file for the hidden simulation component."""

    def __init__(self, filename):
        """Initializes the data class.

        Args:
            filename (str): The name of the main file that data is stored in.
        """
        super().__init__(filename.strip('"\''))
        self.info.attrs['FILE_TYPE'] = 'STANDARD_SIMULATION'
        if 'user_text' not in self.info.attrs:
            self.info.attrs['user_text'] = 'Hello World!'
        if 'user_option' not in self.info.attrs:
            self.info.attrs['user_option'] = 'A'
        self.load_all()

    def load_all(self):
        """Loads all datasets from the file."""
        _ = self.info
        self.close()
