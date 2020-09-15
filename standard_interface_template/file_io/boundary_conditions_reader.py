"""Reads a Standard Interface Template boundary conditions file."""
# 1. Standard python modules
import shlex

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class BoundaryConditionsReader:
    """A class for reading boundary conditions data."""

    def __init__(self):
        """Boundary conditions reader constructor."""
        self.data = {'comp_id': [], 'user_option': [], 'user_text': []}
        self.arcs = {}
        self.nodes = []

    def read(self, filename):
        """Reads the file.

        Args:
            filename (str): The name of the file to read.
        """
        with open(filename) as file:
            arc_id = 0
            for line in file:
                if line.startswith('#'):
                    continue
                line_parts = shlex.split(line)
                card = line_parts[0]
                if card == 'BC':
                    arc_id = int(line_parts[1])
                    user_type = line_parts[2]
                    user_text = line_parts[3]
                    self.data['comp_id'].append(arc_id)
                    self.data['user_option'].append(user_type)
                    self.data['user_text'].append(user_text)
                elif card == 'Points:':
                    grid_points = [int(point) - 1 for point in line_parts[1:]]
                    self.arcs[arc_id] = grid_points
                    self.nodes.extend(grid_points)
