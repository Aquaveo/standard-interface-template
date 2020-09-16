"""Coverage data class."""
# 1. Standard python modules

# 2. Third party modules
import pandas as pd

# 3. Aquaveo modules
from xmscomponents.bases.xarray_base import XarrayBase

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsCoverageData(XarrayBase):
    """Manages data file for the hidden coverage component."""
    display_list = ['A', 'B', 'C']
    unassigned_mat = 0
    column_id = 0
    column_name = 1
    column_user_option = 2
    column_user_text = 3
    column_texture = 4
    column_red = 5
    column_green = 6
    column_blue = 7

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
            xarray.Dataset: The cov_data list dataset
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
            xarray.Dataset: The coverage dataset
        """
        default_data = {'material_id': [0], 'name': 'unassigned', 'user_option': 'A', 'user_text': 'Hello World!',
                        'texture': [1], 'red': [0], 'green': [0], 'blue': [0]}
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
