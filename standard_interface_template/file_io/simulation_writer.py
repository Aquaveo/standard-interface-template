"""Exports Standard Interface Template simulation."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationWriter:
    """A class for writing out simulation data for the Standard Interface Template."""
    def __init__(self, file_name, simulation_data, other_files):
        """Constructor.

        Args:
            file_name (str): The name of the file to write.
            simulation_data (:obj:`SimulationComponent`): The simulation to export.
            other_files (:obj:`list`): The other files that were written for this simulation.
        """
        self._file_name = file_name
        self._data = simulation_data
        self._other_files = other_files

    def write(self):
        """Write the simulation file."""
        with open(self._file_name, 'w') as file:
            file.write('###This is a simulation file for Standard Interface Template.###\n')
            file.write(f"Simulation_Properties: {self._data.data.info.attrs['user_option']}"
                       f" \"{self._data.data.info.attrs['user_text']}\"\n")
            for other_file in self._other_files:
                file.write(f'{other_file}\n')
