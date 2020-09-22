"""This is a class that helps with getting a next color for display options."""

# 1. Standard python modules

# 2. Third party modules
from PySide2.QtGui import QColor

# 3. Aquaveo modules
from xmsguipy.data.polygon_texture import PolygonTexture

# 4. Local modules


class ColorList:
    """A list of colors and a way to generate a next color and texture combination.

    Attributes:
        colors (:obj:`list`): List of colors used.
    """
    colors = [QColor(0, 0, 0),
              QColor(170, 0, 0),
              QColor(0, 85, 0),
              QColor(170, 85, 0),
              QColor(0, 170, 0),
              QColor(170, 170, 0),
              QColor(0, 255, 0),
              QColor(170, 255, 0),
              QColor(0, 0, 127),
              QColor(170, 0, 127),
              QColor(0, 85, 127),
              QColor(170, 85, 127),
              QColor(0, 170, 127),
              QColor(170, 170, 127),
              QColor(0, 255, 127),
              QColor(170, 255, 127),
              QColor(0, 0, 255),
              QColor(170, 0, 255),
              QColor(0, 85, 255),
              QColor(170, 85, 255),
              QColor(0, 170, 255),
              QColor(170, 170, 255),
              QColor(0, 255, 255),
              QColor(170, 255, 255),
              QColor(85, 0, 0),
              QColor(255, 0, 0),
              QColor(85, 85, 0),
              QColor(255, 85, 0),
              QColor(85, 170, 0),
              QColor(255, 170, 0),
              QColor(85, 255, 0),
              QColor(255, 255, 0),
              QColor(85, 0, 127),
              QColor(255, 0, 127),
              QColor(85, 85, 127),
              QColor(255, 85, 127),
              QColor(85, 170, 127),
              QColor(255, 170, 127),
              QColor(85, 255, 127),
              QColor(255, 255, 127),
              QColor(85, 0, 255),
              QColor(255, 0, 255),
              QColor(85, 85, 255),
              QColor(255, 85, 255),
              QColor(85, 170, 255),
              QColor(255, 170, 255),
              QColor(85, 255, 255),
              QColor(255, 255, 255)]

    @classmethod
    def get_next_color_and_texture(cls, new_id, option):
        """Sets the color and texture for a polygon option.

        Args:
            new_id (int): The new id for the polygon display option.
            option (:obj:`PolygonOption`): The polygon display option to set.
        """
        num_colors = len(cls.colors)
        option.color = cls.colors[new_id % num_colors]
        option.texture = PolygonTexture((int(option.texture) + int(new_id / num_colors)) % len(PolygonTexture))
