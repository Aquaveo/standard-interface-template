"""Coverage data class."""
# 1. Standard python modules

# 2. Third party modules
import pandas as pd

# 3. Aquaveo modules
from xmscomponents.bases.xarray_base import XarrayBase

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class BoundaryCoverageData(XarrayBase):
    """Manages data file for the hidden coverage component.

    Attributes:
        display_list (:obj:`list` of str): The list of options the user can choose from.
    """
    display_list = ['A', 'B', 'C']

    def __init__(self, filename):
        """Initializes the data class.

        Args:
            filename (str): The name of the main file that data is stored in.
        """
        self._cov_data = None
        super().__init__(filename.strip('"\''))
        self.info.attrs['FILE_TYPE'] = 'STANDARD_COVERAGE'
        if 'cov_uuid' not in self.info.attrs:
            self.info.attrs['cov_uuid'] = ''  # gets set later
        else:
            self.cov_uuid = self.info.attrs['cov_uuid']
        if 'display_uuid' not in self.info.attrs:
            self.info.attrs['display_uuid'] = ''
        else:
            self.display_uuid = self.info.attrs['display_uuid']
        self.load_all()

    def load_all(self):
        """Loads all datasets from the file."""
        _ = self.info
        _ = self.coverage_data
        self.close()

    @property
    def coverage_data(self):
        """Get the coverage dataset.

        Returns:
            (:obj:`xarray.Dataset`): The cov_data list dataset.
        """
        if self._cov_data is None:
            self._cov_data = self.get_dataset('cov_data', False)
            if self._cov_data is None:
                self._cov_data = self._default_cov_data()
        return self._cov_data

    @coverage_data.setter
    def coverage_data(self, value):
        """Sets the coverage data.

        Args:
            value: The coverage data.
        """
        self._cov_data = value

    @staticmethod
    def _default_cov_data():
        """Creates a default coverage data set.

        Returns:
            (:obj:`xarray.Dataset`): The coverage dataset.
        """
        default_data = {'comp_id': [0], 'user_option': 'A', 'user_text': 'Hello World!'}
        return pd.DataFrame(default_data).to_xarray()

    def commit(self):
        """Save in memory datasets to the NetCDF file."""
        super().commit()

        self._drop_h5_groups(['cov_data'])
        # write
        if self._cov_data is not None:
            self._cov_data.to_netcdf(self._filename, group='cov_data', mode='a')

    def close(self):
        """Closes the H5 file and does not write any data that is in memory."""
        super().close()
        if self._cov_data is not None:
            self._cov_data.close()
