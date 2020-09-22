"""This is a widget for displaying and editing material names and display options."""

# 1. Standard python modules

# 2. Third party modules
from PySide2.QtCore import QItemSelectionModel, Qt, Signal

# 3. Aquaveo modules
from xmsguipy.data.polygon_texture import PolygonOptions
from xmsguipy.delegates.display_option import DisplayOptionDelegate
from xmsguipy.delegates.qx_cbx_delegate import QxCbxDelegate
from xmsguipy.models.qx_pandas_table_model import QxPandasTableModel
from xmsguipy.widgets.basic_table_widget import BasicTableWidget

# 4. Local modules
from standard_interface_template.data.materials_coverage_data import MaterialsCoverageData
from standard_interface_template.gui.widgets.color_list import ColorList
from standard_interface_template.gui.widgets.material_filter_model import MaterialFilterModel


class MaterialTableWidget(BasicTableWidget):
    """Material table widget class.

    Attributes:
        MAT_DISPLAY_COL (int): Column index of the display column.
        MAT_NAME_COL (int): Column index of the name column.
        added (:obj:`Signal`): Signal for when a material is added.
        deleted (:obj:`Signal`): Signal for when a material is deleted.
    """
    MAT_DISPLAY_COL = 0
    MAT_NAME_COL = 1
    added = Signal(int)
    deleted = Signal(list)

    def __init__(self, parent, data):
        """Construct the widget.

        Args:
            parent (:obj:`QObject`): The parent object.
            data (:obj:`pandas.DataFrame`): The material data frame.
        """
        super().__init__(parent)
        self.model = None
        self.data = data
        self.setup_table_model()
        cbx_delegate = QxCbxDelegate(self)
        cbx_delegate.set_strings(MaterialsCoverageData.display_list)
        super()._setup_ui({0: DisplayOptionDelegate(self), 2: cbx_delegate}, True, False, self.filter_model)
        self.table_view.verticalHeader().hide()

    def setup_table_model(self):
        """Sets up the model from the material objects."""
        self.model = QxPandasTableModel(self.data)

        # Override filter model to enable editing of description.
        self.filter_model = MaterialFilterModel(self)
        self.filter_model.setSourceModel(self.model)

    def on_btn_add_row(self):
        """Called when a new row is added to the table."""
        mat_id = max(self.model.data_frame['material_id']) + 1
        description = self._get_new_material_name()
        display = PolygonOptions()
        ColorList.get_next_color_and_texture(mat_id, display)
        self.model.set_default_values({
            'material_id': mat_id,
            'name': description,
            'user_option': 'A',
            'user_text': 'Hello World!',
            'texture': int(display.texture),
            'red': display.color.red(),
            'green': display.color.green(),
            'blue': display.color.blue()
        })
        row_idx = self.model.rowCount()
        self.model.insertRows(row_idx, 1)

        new_index = self.model.index(row_idx, self.MAT_DISPLAY_COL)
        self.table_view.selectionModel().setCurrentIndex(
            new_index, QItemSelectionModel.SelectCurrent | QItemSelectionModel.Clear | QItemSelectionModel.Rows
        )
        self.added.emit(mat_id)

    def on_btn_delete_row(self):
        """Called when a row is removed from the table."""
        indices = self.table_view.selectionModel().selectedIndexes()
        next_select_row = -1
        delete_rows = {index.row() if index.isValid() else -1 for index in indices}
        # sort from largest row id to smallest
        sorted(delete_rows, reverse=True)
        deleted_ids = []
        for row in delete_rows:
            if row <= 0:
                break
            next_select_row = row - 1
            mat_id = self.model.data(self.model.index(row, self.MAT_NAME_COL), Qt.UserRole)
            deleted_ids.append(mat_id)
            self.model.removeRows(row, 1)
        if next_select_row >= 0:
            select_index = self.table_view.model().index(next_select_row, self.MAT_NAME_COL)
            self.table_view.selectionModel().setCurrentIndex(
                select_index, QItemSelectionModel.SelectCurrent | QItemSelectionModel.Clear | QItemSelectionModel.Rows
            )
        self.deleted.emit(deleted_ids)

    def _enable_delete(self, selected, deselected):
        """Enable/disable delete row button.

        Args:
            selected (:obj:`QItemSelection`): Selected indices.
            deselected (:obj:`QItemSelection`): Deselected indices, unused.
        """
        indices = selected.indexes()
        enable_delete = False
        if len(indices) > 0 and indices[0].isValid():
            enable_delete = True
        # disable the delete button if the unassigned/OFF material row (0) is selected
        for idx in indices:
            if idx.row() == 0:
                enable_delete = False
                break
        self.toolbar.widgetForAction(self.btn_actions[self.delete_icon]).setEnabled(enable_delete)

    def _get_new_material_name(self):
        """Get a unique name for a new material.

        Returns:
            (str): A new unique material name, with a prefix of 'new material' followed by a number if 'new material'
                   already exists.
        """
        mat_name = 'new material'
        unique = False
        i = 1
        while not unique:
            unique = True
            for row in self.model.data_frame['name']:
                if str(row) == mat_name:
                    unique = False
                    mat_name = f'new material ({i})'
                    i += 1
                    break
        return mat_name
