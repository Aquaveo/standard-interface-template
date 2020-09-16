"""Reads a Standard Interface Template simulation file."""
# 1. Standard python modules
import shlex

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationReader:
    """A class for reading simulation data."""

    def __init__(self):
        """Simulation reader constructor."""
        self.grid_file = ''
        self.materials_file = ''
        self.boundary_file = ''
        self.user_type = 'A'
        self.user_text = 'Hello World!'

    def read(self, filename):
        """Reads the file.

        Args:
            filename (str): The name of the file to read.
        """
        with open(filename) as file:
            for line in file:
                if line.startswith('#'):
                    continue
                line_parts = shlex.split(line)
                card = line_parts[0]
                if card == 'Simulation_Properties:':
                    self.user_type = line_parts[1]
                    self.user_text = line_parts[2]
                elif card == 'Grid':
                    self.grid_file = line_parts[1]
                elif card == 'Materials':
                    self.materials_file = line_parts[1]
                elif card == 'Boundary_Conditions':
                    self.boundary_file = line_parts[1]
