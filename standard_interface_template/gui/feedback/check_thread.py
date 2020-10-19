"""CheckThread class. Runs the model check."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules
from xmsapi.dmi import Query

# 4. Local modules
from standard_interface_template.check.simulation_check import SimulationCheck
from standard_interface_template.components.sim_query_helper import SimQueryHelper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CheckThread:
    """Writes Standard Interface Template input files."""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._query = None
        self._start_context = None
        self._simulation_name = None
        self._sim_query_helper = None
        self.sim_component = None
        self.ugrid = None
        self.grid_units = None
        self.bc_data = None
        self.bc_comp_ids_to_arc_ids = None
        self.mat_data = None

    def run(self):
        """
        Creates the snap preview of coverages onto the mesh.

        Raises:
            (RuntimeError): Failed to check the simulation for errors.
        """
        try:
            self._setup_query()
            self._get_data()

            checker = SimulationCheck(self)
            errors = checker.run_check()
            if errors:
                self._query.set_context(self._root_context)
                self._query.add(errors)
                self._query.send()
        except:  # noqa
            raise RuntimeError('Error checking simulation.')

    def _setup_query(self):
        """Setup communication with XMS."""
        self._query = Query()
        self._query.get_xms_agent().set_retries(1)
        self._root_context = self._query.get_context()
        r = self._query.get('simulation_name')
        self._simulation_name = r['simulation_name'][0].get_as_string()
        self._query.select('StandardInterfaceTemplate#Sim_Manager')
        self._sim_query_helper = SimQueryHelper(self._query)
        self._sim_query_helper.get_geometry(False)
        self._sim_query_helper.get_boundary_conditions_coverage()
        self._sim_query_helper.get_materials_coverage()

    def _get_data(self):
        """Set member variables from data in SimQueryHelper."""
        self.sim_component = self._sim_query_helper.sim_component
        self.grid_units = self._sim_query_helper.grid_units
        if self._sim_query_helper.co_grid:
            self.ugrid = self._sim_query_helper.co_grid.ugrid
        bc = self._sim_query_helper.boundary_conditions_component
        if bc:
            self.bc_data = bc.data
            if bc.cov_uuid in bc.comp_to_xms:
                self.bc_comp_ids_to_arc_ids = bc.comp_to_xms[bc.cov_uuid]
        mat = self._sim_query_helper.material_component
        if mat:
            self.mat_data = mat.data
