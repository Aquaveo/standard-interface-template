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
    """Manages data file for the hidden coverage component.

    Attributes:
        unassigned_material_id (int): The id of the unassigned material.
        display_list (:obj:`list` of str): The list of options the user can choose from.
        column_id (int): The column index of the display column in the dataframe.
        column_name (int): The column index of the name column in the dataframe.
        column_user_option (int): The column index of the user option column in the dataframe.
        column_user_text (int): The column index of the user text column in the dataframe.
        column_texture (int): The column index of the texture column in the dataframe.
        column_red (int): The column index of the red column in the dataframe.
        column_green (int): The column index of the green column in the dataframe.
        column_blue (int): The column index of the blue column in the dataframe.
    """
    unassigned_material_id = -1
    display_list = ['A', 'B', 'C']
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
            value (:obj:): The coverage data.
        """
        self._cov_data = value

    @staticmethod
    def _default_cov_data():
        """Creates a default coverage data set.

        Returns:
            (:obj:`xarray.Dataset`): The coverage dataset.
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
