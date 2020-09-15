"""Reads a Standard Interface Template geometry file."""
# 1. Standard python modules
import logging

# 2. Third party modules

# 3. Aquaveo modules
from xms.constraint.ugrid_builder import UGridBuilder
from xms.core.filesystem import filesystem
from xms.grid.ugrid import UGrid as XmUGrid

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class GeometryReader:
    """A class for reading geometry data."""

    def __init__(self):
        """Geometry reader constructor."""
        self.logger = logging.getLogger('standard_interface_template')
        self.data = {'elements': [], 'nodes': []}  # The data that is read
        self.temp_mesh_file = ''  # Path to the file where the mesh is saved
        self.cogrid = None  # The grid

    def read(self, filename):
        """Reads the file.

        Args:
            filename (str): The name of the file to read.
        """
        with open(filename) as file:
            file.readline()  # skip the header
            num_nodes = int(file.readline().split()[-1])
            # This assumes that all nodes and cells are in id order with no gaps.
            for line in file:
                line_parts = line.split()
                if line_parts[0] == 'Node':
                    self.data['nodes'].append([float(value) for value in line_parts[2:]])
                elif line_parts[0] == 'Cell':
                    self.data['elements'].append([int(value) - 1 for value in line_parts[2:]])
        self._build_mesh()

    def _get_cell_stream(self):
        """Returns the cell stream."""
        cell_stream = []
        for element in self.data['elements']:
            num_points = len(element)
            if num_points == 3:
                cell_stream.extend([XmUGrid.cell_type_enum.TRIANGLE,
                                   3,
                                   element[0], element[1], element[2]])
            elif num_points == 4:
                cell_stream.extend([XmUGrid.cell_type_enum.QUAD,
                                   4,
                                   element[0], element[1], element[2], element[3]])
            else:
                cell_stream.extend([XmUGrid.cell_type_enum.POLYGON, num_points].extend(element))
        return cell_stream

    def _build_mesh(self):
        """Builds the mesh and writes it to disk."""
        self.logger.info('Building the mesh.')
        cell_stream = self._get_cell_stream()
        self.logger.info(f'{cell_stream}.')
        xmugrid = XmUGrid(self.data['nodes'], cell_stream)
        co_builder = UGridBuilder()
        co_builder.set_is_2d()
        co_builder.set_ugrid(xmugrid)
        self.cogrid = co_builder.build_grid()
        self.temp_mesh_file = filesystem.temp_filename()
        self.cogrid.write_to_file(self.temp_mesh_file, True)
