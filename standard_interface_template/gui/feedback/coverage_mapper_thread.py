"""Uses CoverageMapper to map data to a mesh."""
# 1. Standard python modules
import logging

# 2. Third party modules
from PySide2.QtCore import QThread, Signal

# 3. Aquaveo modules

# 4. Local modules
from standard_interface_template.components.sim_query_helper import SimQueryHelper
from standard_interface_template.mapping.coverage_mapper import CoverageMapper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CoverageMapperThread(QThread):
    """Class for mapping material coverage to a mesh for Standard Interface."""
    processing_finished = Signal()

    def __init__(self, query):
        """
        Constructor.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
        """
        super().__init__()
        self._query = query
        self._logger = logging.getLogger('standard_interface_template')

    def run(self):
        """Creates the snap preview of coverages onto the mesh."""
        try:
            query_helper = SimQueryHelper(self._query)

            query_helper.get_uuids_of_existing_mapped_components()
            if not query_helper.get_geometry(False):
                query_helper.remove_existing_mapped_components()
                self._logger.warning('No mesh geometry in the simulation to generate a snap preview.')
                return
            query_helper.get_materials_coverage()
            query_helper.get_boundary_conditions_coverage()

            if not query_helper.material_component and not query_helper.boundary_conditions_component:
                query_helper.remove_existing_mapped_components()
                self._logger.warning('No coverages in the simulation to generate a snap preview.')
                return

            worker = CoverageMapper(query_helper, generate_snap=True)
            worker.do_map()

            query_helper.add_mapped_components_to_xms()

        except:  # noqa
            self._logger.exception('Error generating snap:')
        finally:
            self.processing_finished.emit()
