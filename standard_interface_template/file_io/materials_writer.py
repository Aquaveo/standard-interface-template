"""Exports Standard Interface Template materials."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsWriter:
    """A class for writing out material data for the Standard Interface Template."""
    def __init__(self, file_name, mat_grid_cells, mat_component):
        """
        Constructor.

        Args:
            file_name (str): The name of the file to write.
            mat_grid_cells (:obj:`dict`): The material to cell ids of the grid that use that material.
            mat_component (:obj:`MaterialsCoverageComponent`): The material data to export.
        """
        self._file_name = file_name
        self._data = mat_component
        self._material_to_cells = mat_grid_cells

    def write(self):
        """Write the materials file."""
        with open(self._file_name, 'w') as file:
            file.write('###This is a materials file for Standard Interface Template.###\n')
            mat_ids = list(self._data.data.coverage_data.material_id.values)
            names = list(self._data.data.coverage_data.name.values)
            options = list(self._data.data.coverage_data.user_option.values)
            texts = list(self._data.data.coverage_data.user_text.values)
            for mat_id, name, option, text in zip(mat_ids, names, options, texts):
                file.write(f'Material: "{name}" {option} "{text}"\n')
                if mat_id in self._material_to_cells:
                    file.write('Cells:')
                    for cell_id in self._material_to_cells[mat_id]:
                        file.write(f' {cell_id + 1}')
                    file.write('\n')
