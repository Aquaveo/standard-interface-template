"""Exports Standard Interface Template simulation."""
# 1. Standard python modules
import logging
import os

# 2. Third party modules
from PySide2.QtCore import QThread, Signal

# 3. Aquaveo modules
from xmsapi.dmi import Query  # noqa: I202

# 4. Local modules
from standard_interface_template.components.sim_query_helper import SimQueryHelper
from standard_interface_template.file_io.boundary_conditions_writer import BoundaryConditionsWriter
from standard_interface_template.file_io.geometry_writer import GeometryWriter
from standard_interface_template.file_io.materials_writer import MaterialsWriter
from standard_interface_template.file_io.simulation_writer import SimulationWriter
from standard_interface_template.mapping.coverage_mapper import CoverageMapper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class ExportSimulationRunner(QThread):
    """Class for exporting Standard Interface Template."""
    processing_finished = Signal()

    def __init__(self, out_dir):
        """Constructor.

        Args:
            out_dir (str): output directory
        """
        super().__init__()
        self.out_dir = out_dir
        self.query = None
        self.sim_query_helper = None
        self.coverage_mapper = None
        self._exporter = None
        self.simulation_name = None
        self.sim_component = None
        self._logger = logging.getLogger('standard_interface_template')
        self.files_exported = []

    def run(self):
        """Exports the coverages and the mesh."""
        try:
            self._setup_query()
            self.coverage_mapper.do_map()
            self._do_export()
        except Exception as error:
            self._logger.exception(f'Error exporting simulation: {str(error)}')
            raise error
        finally:
            self.processing_finished.emit()

    def _setup_query(self):
        self._logger.info('Establishing communication with SMS.')
        self.query = Query()
        self.query.get_xms_agent().set_retries(1)
        r = self.query.get('simulation_name')
        self.simulation_name = r['simulation_name'][0].get_as_string()
        r = self.query.get()['none']
        self._simulation_name = r[0].get_simulation_name()
        self.query.select('StandardInterfaceTemplate#Sim_Manager')
        self.sim_query_helper = SimQueryHelper(self.query)
        self.sim_query_helper.get_simulation_data(True)
        self.sim_component = self.sim_query_helper.sim_component
        self.coverage_mapper = CoverageMapper(self.sim_query_helper, generate_snap=False)

    def _do_export(self):
        """Export the simulation."""
        self.export_geometry()
        self.export_materials()
        self.export_boundary_conditions()
        self.export_simulation()

    def export_geometry(self):
        """Exports the Standard Template Interface geometry file."""
        self._logger.info('Writing Standard Interface Template geometry file.')
        co_grid = self.coverage_mapper.co_grid
        if not co_grid:
            err_str = 'No mesh found aborting model export'
            self._logger.error(err_str)
            raise RuntimeError(err_str)
        base_name = f'{self.simulation_name}.example_geometry'
        self.files_exported.append(f'Grid "{base_name}"')
        file_name = os.path.join(self.out_dir, base_name)
        ugrid = co_grid.ugrid
        writer = GeometryWriter(file_name=file_name, grid=ugrid)
        writer.write()
        self._logger.info('Success writing Standard Interface Template geometry file.')

    def export_materials(self):
        """Exports the Standard Template Interface material file."""
        my_dict = self.coverage_mapper.material_comp_id_to_grid_cell_ids
        self._logger.info('Writing Standard Interface Template material file.')
        base_name = f'{self.simulation_name}.example_materials'
        file_name = os.path.join(self.out_dir, base_name)
        self.files_exported.append(f'Materials "{base_name}"')
        writer = MaterialsWriter(file_name=file_name, mat_grid_cells=my_dict,
                                 mat_component=self.sim_query_helper.material_component)
        writer.write()
        self._logger.info('Success writing Standard Interface Template material file.')

    def export_boundary_conditions(self):
        """Exports the Standard Interface Template boundary conditions file."""
        arc_to_grid = self.coverage_mapper.bc_arc_id_to_grid_ids
        arc_to_comp_id = self.coverage_mapper.bc_arc_id_to_comp_id
        self._logger.info('Writing Standard Interface Template boundary conditions file.')
        base_name = f'{self.simulation_name}.example_boundary'
        file_name = os.path.join(self.out_dir, base_name)
        self.files_exported.append(f'Boundary_Conditions "{base_name}"')
        writer = BoundaryConditionsWriter(file_name=file_name, arc_to_ids=arc_to_comp_id, arc_points=arc_to_grid,
                                          bc_component=self.coverage_mapper.bc_component)
        writer.write()
        self._logger.info('Success writing Standard Interface Template boundary conditions file.')

    def export_simulation(self):
        """Exports the Standard Interface Template simulation file."""
        self._logger.info('Writing Standard Interface Template simulation file.')
        base_name = f'{self.simulation_name}.example_simulation'
        file_name = os.path.join(self.out_dir, base_name)
        writer = SimulationWriter(file_name=file_name, simulation_data=self.sim_query_helper.sim_component,
                                  other_files=self.files_exported)
        writer.write()
        self._logger.info('Success writing Standard Interface Template simulation file.')
