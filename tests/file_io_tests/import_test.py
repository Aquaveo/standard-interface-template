"""For testing."""

# 1. Standard python libraries
import os
import unittest

# 2. Third party libraries

# 3. Aquaveo libraries

# 4. Local libraries
from standard_interface_template.file_io.boundary_conditions_reader import BoundaryConditionsReader
from standard_interface_template.file_io.geometry_reader import GeometryReader
from standard_interface_template.file_io.materials_reader import MaterialsReader
from standard_interface_template.file_io.simulation_reader import SimulationReader
from standard_interface_template.simulation_runner.simulation_run import SimulationRun

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class ImportTests(unittest.TestCase):
    """
    Tests the importing the different files.
    """

    @classmethod
    def setUpClass(cls):
        """Sets up the current working directory for all tests in the class."""
        # Change working directory to test location
        os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

    def tearDown(self):
        """Removes all created files after the tests have run."""
        os.system('git clean -f -d')  # Clean up unversioned files

    def test_import_simulation_file(self):
        """Tests importing the simulation file."""
        folder = 'import_simulation'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        input_file = os.path.join(input_folder, 'test.example_simulation')
        reader = SimulationReader()
        reader.read(input_file)
        self.assertEqual(reader.grid_file, 'test.example_geometry')
        self.assertEqual(reader.materials_file, 'test.example_materials')
        self.assertEqual(reader.boundary_file, 'test.example_boundary')
        self.assertEqual(reader.user_type, 'C')
        self.assertEqual(reader.user_text, 'For testing!')

    def test_import_boundary_conditions_file(self):
        """Tests importing the boundary conditions file."""
        folder = 'import_boundary_conditions'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        input_file = os.path.join(input_folder, 'test.example_boundary')
        reader = BoundaryConditionsReader()
        reader.read(input_file)
        self.assertEqual(reader.arcs, {1: [18, 19, 20]})
        self.assertEqual(reader.data, {'comp_id': [1], 'user_option': ['C'], 'user_text': ['Hello World!']})
        self.assertEqual(reader.nodes, [18, 19, 20])

    def test_import_materials_file(self):
        """Tests importing the materials file."""
        folder = 'import_materials'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        input_file = os.path.join(input_folder, 'test.example_materials')
        reader = MaterialsReader()
        reader.read(input_file)
        base_data = {'material_id': [0, 1], 'name': ['unassigned', 'new material'],
                     'user_option': ['A', 'B'], 'user_text': ['Hello World!', 'Hello World!'],
                     'texture': [1, 1], 'red': [0, 170], 'green': [0, 0], 'blue': [0, 0]}
        base_cells = {0: [9, 10, 14, 16, 17, 32, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                          57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                          80, 81, 82, 83, 84, 85, 86, 87],
                      1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                          30, 31, 33, 34, 35, 36, 37, 38, 40]}
        self.assertEqual(reader.material_cells, base_cells)
        self.assertEqual(reader.data, base_data)

    def test_import_geometry_file(self):
        """Tests importing the geometry file."""
        folder = 'import_geometry'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        input_file = os.path.join(input_folder, 'test.example_geometry')
        reader = GeometryReader()
        reader.read(input_file)
        geometry = {'elements': [[62, 34, 33], [61, 33, 32], [1, 0, 35], [62, 61, 37], [34, 36, 35], [33, 61, 62],
                                 [62, 36, 34], [32, 60, 61], [59, 31, 30], [30, 29, 58], [28, 57, 29], [39, 60, 59],
                                 [60, 31, 59], [59, 58, 40], [57, 58, 29], [30, 58, 59], [57, 41, 58], [57, 56, 42],
                                 [31, 60, 32], [61, 60, 38], [1, 36, 3], [1, 35, 36], [37, 38, 5], [36, 62, 37],
                                 [38, 37, 61], [36, 37, 4], [3, 2, 1], [5, 4, 37], [3, 36, 4], [38, 6, 5], [39, 40, 7],
                                 [60, 39, 38], [41, 42, 9], [59, 40, 39], [41, 40, 58], [40, 41, 8], [7, 6, 39],
                                 [9, 8, 41], [7, 40, 8], [9, 42, 10], [39, 6, 38], [57, 42, 41], [56, 57, 28],
                                 [27, 26, 55], [26, 25, 54], [53, 25, 24], [55, 43, 56], [55, 56, 27], [44, 55, 54],
                                 [53, 54, 25], [55, 26, 54], [54, 53, 45], [24, 52, 53], [27, 56, 28], [51, 23, 22],
                                 [22, 21, 50], [20, 19, 21], [47, 52, 51], [52, 23, 51], [51, 50, 48], [21, 49, 50],
                                 [22, 50, 51], [53, 52, 46], [23, 52, 24], [49, 21, 19], [11, 43, 44], [44, 43, 55],
                                 [45, 46, 13], [45, 44, 54], [53, 46, 45], [12, 44, 45], [11, 10, 43], [13, 12, 45],
                                 [11, 44, 12], [46, 14, 13], [10, 42, 43], [15, 14, 47], [47, 14, 46], [15, 47, 48],
                                 [49, 48, 50], [46, 52, 47], [16, 48, 49], [16, 15, 48], [17, 49, 19], [16, 49, 17],
                                 [19, 18, 17], [51, 48, 47], [43, 42, 56]],
                    'nodes': [[-43.47, 42.53, 0.0], [-43.375, 52.49, 0.0], [-43.28, 62.45, 0.0],
                              [-33.299375, 62.45, 0.0], [-23.31875, 62.45, 0.0], [-13.338125, 62.45, 0.0],
                              [-3.3575, 62.45, 0.0], [6.623125, 62.45, 0.0], [16.60375, 62.45, 0.0],
                              [26.584375, 62.45, 0.0], [36.565, 62.45, 0.0], [46.545625, 62.45, 0.0],
                              [56.52625, 62.45, 0.0], [66.506875, 62.45, 0.0], [76.4875, 62.45, 0.0],
                              [86.468125, 62.45, 0.0], [96.44875, 62.45, 0.0], [106.429375, 62.45, 0.0],
                              [116.41, 62.45, 0.0], [116.41, 52.21, 0.0], [116.41, 41.97, 0.0], [106.4175, 42.005, 0.0],
                              [96.425, 42.04, 0.0], [86.4325, 42.075, 0.0], [76.44, 42.11, 0.0], [66.4475, 42.145, 0.0],
                              [56.455, 42.18, 0.0], [46.4625, 42.215, 0.0], [36.47, 42.25, 0.0], [26.4775, 42.285, 0.0],
                              [16.485, 42.32, 0.0], [6.4925, 42.355, 0.0], [-3.5, 42.39, 0.0], [-13.4925, 42.425, 0.0],
                              [-23.485, 42.46, 0.0], [-33.4775, 42.495, 0.0], [-30.54837280436, 52.854478318506, 0.0],
                              [-19.765637336, 55.551032850956, 0.0], [-9.498252967712, 55.509333065262, 0.0],
                              [0.6177816663962, 55.491368592683, 0.0], [10.710470891368, 55.482000960154, 0.0],
                              [20.799199208211, 55.471917248318, 0.0], [30.887100016142, 55.461761653708, 0.0],
                              [40.974868949456, 55.451573296517, 0.0], [51.062683044196, 55.441340293023, 0.0],
                              [61.150582483265, 55.430980603987, 0.0], [71.238525656438, 55.420106458572, 0.0],
                              [81.380857716132, 55.404900011725, 0.0], [91.445024427909, 55.458469472046, 0.0],
                              [103.18594462147, 53.71996011932, 0.0], [97.87927030652, 49.052160834929, 0.0],
                              [88.79881546806, 49.267571818292, 0.0], [78.848290009109, 49.303857286969, 0.0],
                              [68.780534866657, 49.329314531248, 0.0], [58.692694377572, 49.356594766506, 0.0],
                              [48.601605415271, 49.383413531403, 0.0], [38.509826444047, 49.410183797958, 0.0],
                              [28.417902701242, 49.436951072754, 0.0], [18.32594319008, 49.463756768982, 0.0],
                              [8.2337832786728, 49.490695604141, 0.0], [-1.828831538343, 49.516509883456, 0.0],
                              [-11.88125713462, 49.553336459583, 0.0], [-20.9969686007, 49.364457865513, 0.0]]}
        self.assertEqual(reader.data, geometry)

    def test_import_solution_file(self):
        """Tests importing the solution file."""
        folder = 'import_solution'
        input_folder = os.path.join(os.getcwd(), 'input', folder)
        reader = SimulationRun()
        reader.simulation_name = 'test'
        scalar_values = reader.read_solution_scalar_values(input_folder)
        # The file we are reading has 63 values in it; all of them are 0.0.
        self.assertEqual(scalar_values, [0.0] * 63)
