"""CheckSimulation class."""
# 1. Standard python modules
import os

# 2. Third party modules

# 3. Aquaveo modules
from xmsapi.dmi import ModelCheckError

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationCheck:
    """Model check for Standard Interface Template simulation."""

    def __init__(self, check_thread):
        """Constructor.

        Args:
            check_thread (:obj:`CheckThread`): A class for holding the data that will be used for checking this
                                               simulation.
        """
        super().__init__()
        self.errors = []
        self.error_text = ''
        self._model_control = None
        self._sim_comp_dir = ''
        if check_thread.sim_component:
            self._model_control = check_thread.sim_component.data
            self._sim_comp_dir = os.path.dirname(check_thread.sim_component.main_file)
        self._ugrid = check_thread.ugrid
        self._grid_units = check_thread.grid_units
        self._bc_data = check_thread.bc_data
        self._bc_comp_id_to_arc_id = check_thread.bc_comp_ids_to_arc_ids
        self._mat_data = check_thread.mat_data

    def run_check(self):
        """Runs model check on the simulation."""
        try:
            self._check_mesh()
            self._check_bcs()
            self._check_materials()
        except:  # pragma: no cover # noqa
            raise RuntimeError('Error checking simulation.')
        return self.errors

    def _add_error(self, problem, description, fix):
        """Adds a model check error.

        Args:
            problem (str): An explanation of the problem that has been discovered.
            description (str): A description of the problem.
            fix (str): An explanation of how to fix the problem.
        """
        error = ModelCheckError()
        error.set_problem_text(problem)
        error.set_description_text(description)
        error.set_fix_text(fix)
        self.errors.append({"#description": "ModelCheck", "": error})
        self.error_text = f'{self.error_text}' \
                          f'Problem: {problem}\n' \
                          f'Description: {description}\n' \
                          f'Fix: {fix}\n'

    def _check_mesh(self):
        """Check metrics on the mesh."""
        # make sure a mesh is in the simulation
        if not self._ugrid:
            problem = 'STOP! Simulation requires an unstructured mesh.'
            description = 'An unstructured mesh is required for this simulation.'
            fix = 'Add an unstructured mesh to the simulation.'
            self._add_error(problem, description, fix)
            return

        # check the number of elements in the mesh
        num_cells = self._ugrid.cell_count
        if num_cells < 200000:
            pass
        else:
            problem = f'Warning: The unstructured mesh contains {num_cells} elements.'
            if num_cells < 500000:
                description = 'Best performance for Standard Template Interface occurs with meshes with under ' \
                              '100,000 elements.'
                fix = 'Review the mesh and verify that this many elements is required.'
            elif num_cells < 2000000:
                description = 'Poor performance for Standard Template Interface will occur with this mesh.'
                fix = 'You are STRONGLY encouraged to reduce the number of elements in the mesh.'
            else:
                description = 'The existing mesh greatly exceeds the maximum number of elements.'
                fix = 'Reduce the number of elements to get a workable solution.'
            self._add_error(problem, description, fix)

        # check the units for the mesh (must be feet or meters)
        if not self._grid_units:
            problem = 'STOP! Horizontal units are not FEET or METERS.'
            description = 'Horizontal units must be FEET or METERS for this simulation.'
            fix = 'Change the horizontal units to FEET or METERS.'
            self._add_error(problem, description, fix)

    def _check_bcs(self):
        """Check the boundary conditions."""
        # bc coverage must exist in the simulation
        if not self._bc_data:
            problem = 'STOP! A boundary condition coverage must be included in simulation.'
            description = 'A boundary condition coverage is required for this simulation.'
            fix = 'Add a boundary condition coverage to the simulation.'
            self._add_error(problem, description, fix)
            return

    def _check_materials(self):
        """Check the material properties."""
        # material coverage must exist in the simulation
        if not self._mat_data:
            problem = 'STOP! A material coverage must be included in simulation.'
            description = 'A material coverage is required for this simulation.'
            fix = 'Add a material coverage to the simulation.'
            self._add_error(problem, description, fix)
            return

        # must have material defined in addition to 'unassigned'
        df = self._mat_data.coverage_data.to_dataframe()
        mat_names = df['name'].to_list()
        if len(mat_names) < 2:
            problem = 'STOP! No user defined material zones found.'
            description = 'User defined materials are required for this simulation.'
            fix = 'Define materials for the material coverage.'
            self._add_error(problem, description, fix)

        # material names must be unique
        unique_names = set(mat_names)
        if len(mat_names) != len(unique_names):
            problem = 'STOP! Material names must be unique.'
            description = 'Standard Interface Template requires unique material names.'
            fix = 'Define unique material names for the material coverage.'
            self._add_error(problem, description, fix)
