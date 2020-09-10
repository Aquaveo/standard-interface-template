"""Uses CoverageMapper to map data to a mesh."""
# 1. Standard python modules
import logging

# 2. Third party modules
from PySide2.QtCore import QThread, Signal

# 3. Aquaveo modules

# 4. Local modules
from standard_interface_template.mapping.coverage_mapper import CoverageMapper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CoverageMapperRunner(QThread):
    """Class for mapping material coverage to a mesh for Standard Interface."""
    processing_finished = Signal()

    def __init__(self, query):
        """Constructor."""
        super().__init__()
        self._query = query
        self._logger = logging.getLogger('standard_interface_template')

    def run(self):
        """Creates the snap preview of coverages onto the mesh."""
        try:
            query_helper = SimQueryHelper(self._query)
            query_helper.get_sim_data(True)

            worker = CoverageMapper(query_helper, generate_snap=True)
            worker.do_map()

            query_helper.mapped_comps = worker.mapped_comps
            query_helper.add_mapped_components_to_xms()
        except:  # noqa
            self._logger.exception('Error generating snap.')
        finally:
            self.processing_finished.emit()
