"""For testing."""

# 1. Standard python libraries
import filecmp
import os
import unittest

# 2. Third party libraries

# 3. Aquaveo libraries
from xms.constraint import read_grid_from_file

# 4. Local libraries
from standard_interface_template.components.boundary_coverage_component import BoundaryCoverageComponent
from standard_interface_template.components.materials_coverage_component import MaterialsCoverageComponent
from standard_interface_template.components.simulation_component import SimulationComponent
from standard_interface_template.file_io.boundary_conditions_writer import BoundaryConditionsWriter
from standard_interface_template.file_io.geometry_writer import GeometryWriter
from standard_interface_template.file_io.materials_writer import MaterialsWriter
from standard_interface_template.file_io.simulation_writer import SimulationWriter

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class ExportTests(unittest.TestCase):
    """
    Tests the exporting the different files.
    """

    @classmethod
    def setUpClass(cls):
        """Sets up the current working directory for all tests in the class."""
        # Change working directory to test location
        os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

    def tearDown(self):
        """Removes all created files after the tests have run."""
        os.system('git clean -f -d')  # Clean up unversioned files

    def setUp(self):
        """Sets up each individual test."""
        # Clear the cache in case something was there.
        filecmp.clear_cache()

    def test_export_simulation_file(self):
        """Tests exporting the simulation file."""
        folder = 'export_simulation'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        baseline_folder = os.path.join(os.getcwd(), 'baselines', folder)
        sim_component_file = os.path.join(input_folder, 'sim_comp.nc')
        sim_data = SimulationComponent(sim_component_file)
        output_file = 'test.example_simulation'
        writer = SimulationWriter(output_file, sim_data, ['Grid "test.example_geometry"',
                                                          'Materials "test.example_materials"',
                                                          'Boundary_Conditions "test.example_boundary"'])
        writer.write()
        self.assertTrue(filecmp.cmp(output_file, os.path.join(baseline_folder, output_file)))

    def test_export_boundary_conditions_file(self):
        """Tests exporting the boundary conditions file."""
        folder = 'export_boundary_conditions'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        baseline_folder = os.path.join(os.getcwd(), 'baselines', folder)
        bc_component_file = os.path.join(input_folder, 'boundary_coverage_comp.nc')
        bc_data = BoundaryCoverageComponent(bc_component_file)
        output_file = 'test.example_boundary'
        arc_to_ids = {1: 1}
        arc_points = {1: (18, 19, 20)}
        writer = BoundaryConditionsWriter(output_file, arc_to_ids, arc_points, bc_data)
        writer.write()
        self.assertTrue(filecmp.cmp(output_file, os.path.join(baseline_folder, output_file)))

    def test_export_materials_file(self):
        """Tests exporting the materials file."""
        folder = 'export_materials'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        baseline_folder = os.path.join(os.getcwd(), 'baselines', folder)
        mat_component_file = os.path.join(input_folder, 'materials_coverage_comp.nc')
        mat_data = MaterialsCoverageComponent(mat_component_file)
        output_file = 'test.example_materials'
        mat_to_cells = {1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                            30, 31, 33, 34, 35, 36, 37, 38, 40],
                        0: [9, 10, 14, 16, 17, 32, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                            57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                            80, 81, 82, 83, 84, 85, 86, 87]}
        writer = MaterialsWriter(output_file, mat_to_cells, mat_data)
        writer.write()
        self.assertTrue(filecmp.cmp(output_file, os.path.join(baseline_folder, output_file)))

    def test_export_geometry_file(self):
        """Tests exporting the geometry file."""
        folder = 'export_geometry'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        baseline_folder = os.path.join(os.getcwd(), 'baselines', folder)
        # To export an *.xmc file from XMS for a test, convert the geometry to a UGrid.
        # On the Ugrid, right-click and choose "Export...".
        grid_file = os.path.join(input_folder, 'grid.xmc')
        grid = read_grid_from_file(grid_file)
        output_file = 'test.example_geometry'
        writer = GeometryWriter(output_file, grid.ugrid)
        writer.write()
        self.assertTrue(filecmp.cmp(output_file, os.path.join(baseline_folder, output_file)))
