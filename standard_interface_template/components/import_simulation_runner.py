"""Imports a Standard Interface Template simulation."""
# 1. Standard python modules
import logging
import os
import shutil
import uuid

# 2. Third party modules
import pandas
from PySide2.QtCore import QThread, Signal

# 3. Aquaveo modules
from data_objects.parameters import Arc, Component, Coverage, Point, Simulation, UGrid
from xmsapi.dmi import Query
from xmscomponents.display.display_options_io import write_display_option_ids
from xmscoverage.grid.grid_cell_to_polygon_coverage_builder import GridCellToPolygonCoverageBuilder

# 4. Local modules
from standard_interface_template.components.boundary_coverage_component import (BoundaryCoverageComponent,
                                                                                BC_COVERAGE_INITIAL_ATT_ID_FILE,
                                                                                BC_COVERAGE_INITIAL_COMP_ID_FILE)
from standard_interface_template.components.coverage_arc_builder import CoverageArcBuilder
from standard_interface_template.components.materials_coverage_component import (MaterialsCoverageComponent,
                                                                                 MAT_COVERAGE_INITIAL_ATT_ID_FILE,
                                                                                 MAT_COVERAGE_INITIAL_COMP_ID_FILE)
from standard_interface_template.data.simulation_data import SimulationData
from standard_interface_template.file_io.boundary_conditions_reader import BoundaryConditionsReader
from standard_interface_template.file_io.geometry_reader import GeometryReader
from standard_interface_template.file_io.materials_reader import MaterialsReader
from standard_interface_template.file_io.simulation_reader import SimulationReader


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class ImportSimulationRunner(QThread):
    """Read an Standard Interface Template simulation when a *.example_simulation file is opened in SMS."""
    processing_finished = Signal()

    def __init__(self, xms_data=None):
        """Construct the Importer.

        Args:
            xms_data (dict): XMS data dictionary. Useful for testing because it will avoid any Query calls.
                {
                    'filename': '',  # Path to the *.example_simulation file to read
                    'comp_dir': '',  # Path to the XMS "Components" temp folder
                }

        """
        super().__init__()
        self._logger = logging.getLogger('standard_interface_template')
        self._xms_data = xms_data
        self._query = None
        self._root_idx = -1
        self._build_vertices = []

        self._boundary_conditions_reader = None
        self._geometry_reader = None
        self._materials_reader = None
        self._simulation_reader = None

        # Stuff we will be sending back to XMS
        self._sim_comp = None
        self._mesh = None
        self._bc_cov = None
        self._bc_do_comp = None  # data_object for BC coverage component
        self._mat_cov = None
        self._mat_do_comp = None  # data_object for Material coverage component

        if not self._xms_data:
            self._get_xms_data()

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

            # Add a new Standard Interface Template simulation
            sim = Simulation()
            sim.set_model_name("StandardInterfaceTemplate")
            sim.set_simulation_name('Sim')
            arg_list = [{"none": sim, "#description": "Build"}]
            place_marks = self._query.add(arg_list)
            if place_marks:
                self._root_idx = place_marks[0]

            # Get the SMS temp directory
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

    def _add_xms_data(self):
        """Send imported data to SMS."""
        self._logger.info('Preparing to send imported data to SMS...')

        sim_comp_idx = None
        if self._sim_comp:
            # Add the hidden simulation component
            arg_list = [{'#description': 'StandardInterfaceTemplate#Sim_Manager', '': self._sim_comp}]
            place_marks = self._query.add(arg_list, self._root_idx)
            if place_marks:
                sim_comp_idx = place_marks[0]
                self._build_vertices.append(sim_comp_idx)
            else:
                raise RuntimeError("Could not create Standard Interface Template simulation.")

        if self._mesh:
            # add the mesh to the Query Context
            mesh_list = [{'#description': 'BuildNoTake', 'Geometry': self._mesh}]
            self._query.add(mesh_list, self._root_idx)
            take_list = [{'#description': 'AddTakeUuid', '': self._mesh.get_uuid()}]
            self._build_vertices.extend(self._query.add(take_list))

        if self._bc_cov:
            # Add the Boundary Conditions coverage geometry and its hidden component.
            self._build_vertices.extend(self._query.add([{
                '#description': 'BuildNoTake',
                'Coverage': self._bc_cov,
                'COVERAGE_TYPE': 'StandardInterfaceTemplate#Boundary Conditions Coverage'
            }], self._root_idx))
            if self._bc_do_comp:
                # Add the Boundary Conditions coverage's hidden component
                self._build_vertices.extend(
                    self._query.add([{
                        '#description': 'StandardInterfaceTemplate#Boundary_Coverage_Component',
                        '': self._bc_do_comp
                    }], self._build_vertices[-1])
                )
            arg_list = [{"": self._bc_cov.get_uuid(), "#description": "AddTakeUuid"}]
            if sim_comp_idx is not None:
                self._build_vertices.extend(self._query.add(arg_list, sim_comp_idx))

        if self._mat_cov:
            # Add the materials coverage geometry and its hidden component.
            if self._mat_cov:
                self._build_vertices.extend(self._query.add([{
                    '#description': 'BuildNoTake',
                    'Coverage': self._mat_cov,
                    'COVERAGE_TYPE': 'StandardInterfaceTemplate#Materials Coverage'
                }], self._root_idx))
                if self._mat_do_comp:
                    # Add the material coverage's hidden component.
                    self._build_vertices.extend(
                        self._query.add([{
                            '#description': 'StandardInterfaceTemplate#Materials_Coverage_Component',
                            '': self._mat_do_comp
                        }], self._build_vertices[-1])
                    )
                # Link the materials coverage to the simulation
                arg_list = [{"": self._mat_cov.get_uuid(), "#description": "AddTakeUuid"}]
                if sim_comp_idx is not None:
                    self._build_vertices.extend(self._query.add(arg_list, sim_comp_idx))
        self.send()

    def _read_boundary_conditions(self, filename):
        """Read parameters from a *.example_boundary file.

        Args:
            filename (str): Filepath of the *.example_geometry file
        """
        self._boundary_conditions_reader = BoundaryConditionsReader()
        self._boundary_conditions_reader.read(filename)

        self._build_bc_coverage()

        comp_uuid = str(uuid.uuid4())
        bc_comp_dir = os.path.join(self._xms_data['comp_dir'], comp_uuid)
        os.makedirs(bc_comp_dir, exist_ok=True)
        bc_main_file = os.path.join(bc_comp_dir, 'boundary_coverage_comp.nc')
        bc_component = BoundaryCoverageComponent(bc_main_file)
        bc_df = bc_component.data.coverage_data.to_dataframe()
        column_list = bc_df.columns.tolist()
        bc_df = bc_df.append(pandas.DataFrame.from_dict(self._boundary_conditions_reader.data))[column_list]
        bc_component.data.coverage_data = bc_df.to_xarray()
        bc_component.data.commit()

        # Write component id and BC arc att ids to a file so we can initialize them in get_initial_display_options
        ids = list(bc_component.data.coverage_data.comp_id.values)
        id_file = os.path.join(bc_comp_dir, BC_COVERAGE_INITIAL_ATT_ID_FILE)
        write_display_option_ids(id_file, ids)
        id_file = os.path.join(bc_comp_dir, BC_COVERAGE_INITIAL_COMP_ID_FILE)
        write_display_option_ids(id_file, ids)

        self._bc_do_comp = Component()
        self._bc_do_comp.set_uuid(comp_uuid)
        self._bc_do_comp.set_unique_name_and_model_name('Boundary_Coverage_Component', 'StandardInterfaceTemplate')
        self._bc_do_comp.set_main_file(bc_main_file)

    def _read_simulation(self):
        """Read parameters from a *.example_simulation file."""
        self._simulation_reader = SimulationReader()
        self._simulation_reader.read(self._xms_data['filename'])

        comp_uuid = str(uuid.uuid4())
        sim_comp_dir = os.path.join(self._xms_data['comp_dir'], comp_uuid)
        os.makedirs(sim_comp_dir, exist_ok=True)
        sim_main_file = os.path.join(sim_comp_dir, 'sim_comp.nc')
        sim_data = SimulationData(sim_main_file)
        sim_data.info.attrs['user_text'] = self._simulation_reader.user_text
        sim_data.info.attrs['user_option'] = self._simulation_reader.user_type
        sim_data.commit()

        self._sim_comp = Component()
        self._sim_comp.set_uuid(comp_uuid)
        self._sim_comp.set_unique_name_and_model_name('Sim_Manager', 'StandardInterfaceTemplate')
        self._sim_comp.set_main_file(sim_main_file)

    def _read_geometry(self, filename):
        """Read mesh geometry from a *.example_geometry file.

        Args:
            filename (str): Filepath of the *.example_geometry file
        """
        self._geometry_reader = GeometryReader()
        self._geometry_reader.read(filename)

        self._mesh = UGrid(self._geometry_reader.temp_mesh_file)
        self._mesh.set_name('Mesh')
        self._mesh.set_uuid(str(uuid.uuid4()))

    def _read_materials(self, filename):
        """Read material assignments from a *.example_materials file.

        Args:
            filename (str): Filepath of the *.example_materials file.
        """
        self._materials_reader = MaterialsReader()
        self._materials_reader.read(filename)

        # Create a dataset of materials (size of cells)
        cell_materials = [0 for _ in range(self._geometry_reader.cogrid.ugrid.cell_count)]
        for material, cells in self._materials_reader.material_cells.items():
            for cell in cells:
                cell_materials[cell] = material

        cov_name = 'Materials'
        cov_builder = GridCellToPolygonCoverageBuilder(self._geometry_reader.cogrid, cell_materials, None, cov_name)
        new_cov_geom = cov_builder.create_polygons_and_build_coverage()
        new_cov_uuid = new_cov_geom.get_uuid()
        self._mat_cov = new_cov_geom

        comp_uuid = str(uuid.uuid4())
        mat_comp_dir = os.path.join(self._xms_data['comp_dir'], comp_uuid)
        os.makedirs(mat_comp_dir, exist_ok=True)
        mat_main_file = os.path.join(mat_comp_dir, 'materials_coverage_comp.nc')
        mat_component = MaterialsCoverageComponent(mat_main_file)
        mat_component.data.coverage_data = pandas.DataFrame.from_dict(self._materials_reader.data).to_xarray()
        mat_component.data.commit()

        # Write component id and polygon att ids to a file so we can initialize them in get_initial_display_options
        att_ids = []
        comp_ids = []
        for mat_id, poly_ids in cov_builder.dataset_polygon_ids.items():
            if mat_id < 0:  # pragma no cover
                continue  # Don't need to write out unassigned polygons since it is the default category.
            non_default_poly_ids = [poly_id for poly_id in poly_ids if poly_id > 0]
            att_ids.extend(non_default_poly_ids)
            comp_ids.extend([mat_id for _ in range(len(non_default_poly_ids))])
        id_file = os.path.join(mat_comp_dir, MAT_COVERAGE_INITIAL_ATT_ID_FILE)
        write_display_option_ids(id_file, att_ids)
        id_file = os.path.join(mat_comp_dir, MAT_COVERAGE_INITIAL_COMP_ID_FILE)
        write_display_option_ids(id_file, comp_ids)

        self._mat_do_comp = Component()
        self._mat_do_comp.set_uuid(comp_uuid)
        self._mat_do_comp.set_unique_name_and_model_name('Materials_Coverage_Component', 'StandardInterfaceTemplate')
        self._mat_do_comp.set_main_file(mat_main_file)

    def _build_bc_coverage(self):
        """Create the data_objects Boundary Conditions Coverage from data imported from the *.example_boundary file."""
        self._logger.info('Building Boundary Conditions coverage geometry...')
        self._bc_cov = Coverage()
        self._bc_cov.set_name('Boundary Conditions')
        self._bc_cov.set_uuid(str(uuid.uuid4()))
        arc_builder = CoverageArcBuilder(self._geometry_reader.cogrid.ugrid.locations)
        for nodestring_id, nodestring in self._boundary_conditions_reader.arcs.items():
            arc_builder.add_arc(nodestring[0], nodestring[-1], nodestring[1:-1])
        self._bc_cov.set_arcs(arc_builder.arcs)
        self._bc_cov.complete()

    def read(self):
        """Trigger the read of the Standard Interface Template simulation."""
        try:
            self._logger.info('Reading the simulation.')
            self._read_simulation()
            read_directory = os.path.dirname(self._xms_data['filename'])
            self._read_geometry(os.path.join(read_directory, self._simulation_reader.grid_file))
            self._read_boundary_conditions(os.path.join(read_directory, self._simulation_reader.boundary_file))
            self._read_materials(os.path.join(read_directory, self._simulation_reader.materials_file))

            if self._query:
                self._add_xms_data()
        except Exception as error:
            self._logger.exception(f'Error importing simulation: {str(error)}')
            raise error
        finally:
            self.processing_finished.emit()

    def send(self):
        """Send imported data to SMS."""
        if self._query:
            ctxt = self._query.get_context()
            for build_vertex in self._build_vertices:
                ctxt.set_place_mark(build_vertex)
            self._query.set_context(ctxt)
            self._query.send()

    def run(self):
        """Creates coverages, a simulation, and a mesh for SMS."""
        try:
            self.read()
        except Exception as error:
            self._logger.exception(f'Error importing simulation: {str(error)}')
            raise error
        finally:
            self.processing_finished.emit()
