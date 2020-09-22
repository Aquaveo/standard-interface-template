"""Imports a Standard Interface Template simulation."""
# 1. Standard python modules
import os
import shutil

# 2. Third party modules
from PySide2.QtCore import Signal

# 3. Aquaveo modules
from xmsapi.dmi import Query

# 4. Local modules
from standard_interface_template.gui.feedback.import_simulation_thread import ImportSimulationThread


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class ImportGeometryThread(ImportSimulationThread):
    """Read an Standard Interface Template simulation when a *.example_geometry file is opened in XMS."""
    processing_finished = Signal()

    def __init__(self, xms_data=None):
        """Construct the Importer.

        Args:
            xms_data (:obj:`dict`): XMS data dictionary. Useful for testing because it will avoid any Query calls.
                {
                    'filename': '',  # Path to the *.example_simulation file to read
                    'comp_dir': '',  # Path to the XMS "Components" temp folder
                }

        """
        super().__init__(xms_data)

    def _get_xms_data(self):
        """Get all data from XMS needed to import the Standard Interface Template simulation."""
        self._logger.info('Retrieving data from XMS...')
        self._xms_data = {
            'filename': '',
            'comp_dir': '',
        }
        try:
            self._query = Query()
            self._query.get_xms_agent().set_retries(1)
            self._xms_data['filename'] = self._query.get_read_file()

            # Get the XMS temp directory
            start_ctxt = self._query.get_context()
            self._query.select('InstallResources')
            temp_dir = self._query.get('Temporary Directory')['Temporary Directory']
            if not temp_dir or not temp_dir[0]:
                raise RuntimeError("Could not get XMS temporary directory.")
            delete_dir = temp_dir[0].get_as_string()
            self._xms_data['comp_dir'] = os.path.join(os.path.dirname(delete_dir), 'Components')
            shutil.rmtree(delete_dir, ignore_errors=True)
            self._query.set_context(start_ctxt)
        except Exception:
            self._logger.exception(
                'Unable to retrieve data from SMS needed to import Standard Interface Template simulation')

    def read(self):
        """Trigger the read of the Standard Interface Template geometry.

        Raises:
            (Exception): There was a problem reading the geometry file.
        """
        try:
            self._logger.info('Reading the geometry.')
            self._read_geometry(self._xms_data['filename'])

            if self._query:
                self._add_xms_data()
        except Exception as error:
            self._logger.exception(f'Error importing geometry: {str(error)}')
            raise error
        finally:
            self.processing_finished.emit()
