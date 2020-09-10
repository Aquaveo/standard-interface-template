"""This dialog provides a way for the user to choose which material a polygon is assigned to."""

# 1. Standard python modules

# 2. Third party modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QComboBox, QDialogButtonBox, QLabel, QVBoxLayout

# 3. Aquaveo modules
from xmsguipy.dialogs.xms_parent_dlg import XmsDlg

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class AssignPolyMaterialDialog(XmsDlg):
    """A dialog for assigning materials to polygons."""

    def __init__(self, win_cont, icon, title, multi_select_lbl, mat_names, current_mat_idx):
        """Initializes the class, sets up the ui, and loads the simulation.

        Args:
            win_cont (QWidget): Parent window
            icon (QIcon): Window icon
            title (str): Window title
            multi_select_lbl(str): If not empty, will be displayed in a label
            mat_names (list of str): List of the material names
            current_mat_idx (int): Material id of the currently selected polygon if previously assigned

        """
        super().__init__(win_cont, 'standard_interface_template.gui.assign_poly_material_dialog')
        self.multi_select_lbl = multi_select_lbl
        self.widgets = {}

        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)
        self.setup_ui(mat_names, current_mat_idx)

    def setup_ui(self, mat_names, current_idx):
        """Setup dialog widgets.

        Args:
            mat_names (list of str): List of the material names
            current_idx (int): Index in the material list of the currently selected polygon's material if previously
                assigned

        """
        self.widgets['vert_layout'] = QVBoxLayout()
        # Add a label to indicate that this assignment applies to multiple polygons
        self.widgets['lbl_multi_select'] = None
        if self.multi_select_lbl:
            self.widgets['lbl_multi_select'] = QLabel(self.multi_select_lbl)
            self.widgets['vert_layout'].addWidget(self.widgets['lbl_multi_select'])
        # Add a combobox for picking the material type.
        self.widgets['cbx_type'] = QComboBox()
        self.widgets['cbx_type'].addItems(mat_names)
        # Set the current index
        self.widgets['cbx_type'].setCurrentIndex(current_idx)
        self.widgets['vert_layout'].addWidget(self.widgets['cbx_type'])
        # Add Ok and Cancel buttons
        self.widgets['btn_box'] = QDialogButtonBox()
        self.widgets['btn_box'].setOrientation(Qt.Horizontal)
        self.widgets['btn_box'].setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.widgets['btn_box'].accepted.connect(self.accept)
        self.widgets['btn_box'].rejected.connect(self.reject)
        self.widgets['vert_layout'].addWidget(self.widgets['btn_box'])
        self.setLayout(self.widgets['vert_layout'])

    def get_selected_material(self):
        """Returns the currently selected material.

        Returns:
            (int): The currently selected material's index in the material list.

        """
        return self.widgets['cbx_type'].currentIndex()
