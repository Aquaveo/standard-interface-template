"""Reads a Standard Interface Template materials file."""
# 1. Standard python modules
import shlex

# 2. Third party modules

# 3. Aquaveo modules
from xmsguipy.data.polygon_texture import PolygonOptions

# 4. Local modules
from standard_interface_template.gui.widgets.color_list import ColorList


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsReader:
    """A class for reading materials data."""

    def __init__(self):
        """Materials reader constructor."""
        self.material_cells = {}
        self.data = {'material_id': [], 'name': [], 'user_option': [], 'user_text': [],
                     'texture': [], 'red': [], 'green': [], 'blue': []}

    def read(self, filename):
        """Reads the file.

        Args:
            filename (str): The name of the file to read.
        """
        with open(filename) as file:
            # This assumes that the "unassigned" material is first.
            name = ''
            material_id = -1
            for line in file:
                if line.startswith('#'):
                    continue
                line_parts = shlex.split(line)
                card = line_parts[0]
                if card == 'Material:':
                    material_id += 1
                    name = line_parts[1]
                    user_type = line_parts[2]
                    user_text = line_parts[3]
                    self.data['material_id'].append(material_id)
                    self.data['name'].append(name)
                    self.data['user_option'].append(user_type)
                    self.data['user_text'].append(user_text)
                    option = PolygonOptions()
                    ColorList.get_next_color_and_texture(material_id, option)
                    self.data['texture'].append(int(option.texture))
                    self.data['red'].append(option.color.red())
                    self.data['green'].append(option.color.green())
                    self.data['blue'].append(option.color.blue())
                elif card == 'Cells:':
                    grid_cells = [int(point) - 1 for point in line_parts[1:]]
                    self.material_cells[material_id] = grid_cells
