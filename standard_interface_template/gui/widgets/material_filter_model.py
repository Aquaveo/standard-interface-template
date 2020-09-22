"""Filter model for the material properties table."""
# 1. Standard python modules
import typing

# 2. Third party modules
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QColor

# 3. Aquaveo modules
from xmsguipy.data.polygon_texture import PolygonOptions, PolygonTexture
from xmsguipy.models.rename_model import RenameModel

# 4. Local modules
from standard_interface_template.data.materials_coverage_data import MaterialsCoverageData

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialFilterModel(RenameModel):
    """A model to set enabled/disabled states.

    Attributes:
        column_display (int): The column index of the display column.
        column_name (int): The column index of the name column.
        column_user_option (int): The column index of the user option column.
        column_user_text (int): The column index of the user text column.
    """
    column_display = 0
    column_name = 1
    column_user_option = 2
    column_user_text = 3

    def __init__(self, parent=None):
        """Initializes the filter model.

        Args:
            parent (:obj:`QObject`): The parent object.
        """
        super().__init__(['', 'Material Name', 'Material Type', 'Material Text'], parent)

    def flags(self, index):
        """Set flags for an item in the model.

        Args:
            index (:obj:`QModelIndex`): The item's model index.

        Returns:
            (:obj:`Qt.ItemFlags`): Updated flags for the item.
        """
        ret_flags = super().flags(index)
        row = index.row()
        col = index.column()
        unassigned_material_row = 0

        if row == unassigned_material_row and col == MaterialsCoverageData.column_name:
            # Disable editing of the unassigned material name
            ret_flags = ret_flags & (~Qt.ItemIsEditable)
        else:
            ret_flags |= Qt.ItemIsEnabled
        return ret_flags

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        """Override for filter accepts column.

        Args:
            source_column (int): The column from the source model.
            source_parent (:obj:`QModelIndex`): The parent from the source model.

        Returns:
            (bool): True if the column should be displayed.
        """
        if source_column in [MaterialsCoverageData.column_id]:
            return False
        else:
            return True

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        """Gets the data for the model.

        Args:
            index (:obj:`QModelIndex`): The location index in the Qt model.
            role (int): The role the data represents.
        """
        if index.column() == self.column_display:
            if role == Qt.UserRole:
                options = PolygonOptions()
                texture = self.sourceModel().data(self.sourceModel().index(index.row(),
                                                                           MaterialsCoverageData.column_texture),
                                                  Qt.EditRole)
                red = self.sourceModel().data(self.sourceModel().index(index.row(),
                                                                       MaterialsCoverageData.column_red),
                                              Qt.EditRole)
                green = self.sourceModel().data(self.sourceModel().index(index.row(),
                                                                         MaterialsCoverageData.column_green),
                                                Qt.EditRole)
                blue = self.sourceModel().data(self.sourceModel().index(index.row(),
                                                                        MaterialsCoverageData.column_blue),
                                               Qt.EditRole)
                options.texture = PolygonTexture(int(texture))
                options.color = QColor(int(red), int(green), int(blue))
                return options
            elif role in [Qt.EditRole, Qt.DisplayRole]:
                return ''
        return super().data(index, role)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:  # noqa: N802
        """Sets the data for the model.

        Args:
            index (:obj:`QModelIndex`): The location index in the Qt model.
            value (:obj:`typing.Any`): The value to set.
            role (int): The role the data represents.

        Returns:
            (bool): True if successful.
        """
        if index.column() == self.column_display:
            if role == Qt.UserRole:
                texture = self.sourceModel().setData(self.sourceModel().index(index.row(),
                                                                              MaterialsCoverageData.column_texture),
                                                     value.texture, Qt.EditRole)
                red = self.sourceModel().setData(self.sourceModel().index(index.row(),
                                                                          MaterialsCoverageData.column_red),
                                                 value.color.red(), Qt.EditRole)
                green = self.sourceModel().setData(self.sourceModel().index(index.row(),
                                                                            MaterialsCoverageData.column_green),
                                                   value.color.green(), Qt.EditRole)
                blue = self.sourceModel().setData(self.sourceModel().index(index.row(),
                                                                           MaterialsCoverageData.column_blue),
                                                  value.color.blue(), Qt.EditRole)
                return texture and red and green and blue
        return super().setData(index, value, role)

    def columnCount(self, parent: QModelIndex) -> int:  # noqa: N802
        """
        Returns the column count.

        Args:
            parent (:obj:`QModelIndex`): The parent.

        Returns:
            (int): The column count.
        """
        return 4

    def mapFromSource(self, source_index: QModelIndex) -> QModelIndex:  # noqa: N802
        """
        Maps from source model to this model's index.

        Args:
            source_index (:obj:`QModelIndex`): The source model index.

        Returns:
            (:obj:`QModelIndex`): This model's index.
        """
        column_map = {MaterialsCoverageData.column_name: self.column_name,
                      MaterialsCoverageData.column_user_text: self.column_user_text,
                      MaterialsCoverageData.column_user_option: self.column_user_option}
        if source_index.column() in column_map.keys():
            return self.index(source_index.row(), column_map[source_index.column()], source_index.parent())
        return super().mapFromSource(source_index)

    def mapToSource(self, proxy_index: QModelIndex) -> QModelIndex:  # noqa: N802
        """
        Maps from this model's index to the source model's index.

        Args:
            proxy_index (:obj:`QModelIndex`): The proxy model index.

        Returns:
            (:obj:`QModelIndex`): The source model's index.
        """
        column_map = {self.column_name: MaterialsCoverageData.column_name,
                      self.column_user_text: MaterialsCoverageData.column_user_text,
                      self.column_user_option: MaterialsCoverageData.column_user_option}
        if proxy_index.column() in column_map.keys():
            return self.sourceModel().index(proxy_index.row(), column_map[proxy_index.column()], proxy_index.parent())
        return super().mapToSource(proxy_index)
