"""Exports Standard Interface Template geometry."""
# 1. Standard python modules
import logging
import os

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class GeometryWriter:
    """A class for writing out geometry for the Standard Interface Template."""
    def __init__(self, file_name, grid):
        """Constructor.

        Args:
            file_name (str): The name of the file to write.
            grid (xms.grid.ugrid.UGrid): The geometry to export.
        """
        self._file_name = file_name
        self._grid = grid

    def write(self):
        """Write the geometry file."""
        with open(self._file_name, 'w') as file:
            file.write('###This is a geometry file for Standard Interface Template.###\n')
            pts = self._grid.locations
            file.write(f'Number of nodes: {len(pts)}\n')
            for index in range(len(pts)):
                file.write(f'Node {index + 1} {pts[index][0]} {pts[index][1]} {pts[index][2]}\n')

            cell_stream = self._grid.cellstream
            cell_id = 0
            i = 0
            while i < len(cell_stream):
                cell_id += 1
                num_pts = int(cell_stream[i + 1])
                file.write(f'Cell {cell_id}')
                for offset in range(2, 2 + num_pts):
                    file.write(f' {cell_stream[i + offset] + 1}')
                file.write('\n')
                i += num_pts + 2
