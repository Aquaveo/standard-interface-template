"""Dialog for assigning Material coverage properties."""
# 1. Standard python modules
import webbrowser

# 2. Third party modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QStyle, QVBoxLayout

# 3. Aquaveo modules

# 4. Local modules
from standard_interface_template.gui.widgets.material_table_widget import MaterialTableWidget

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsDialog(QDialog):
    """A dialog to define materials and their properties."""

    def __init__(self, title, win_cont, icon, data):
        """Initializes the material list and properties dialog.

        Args:
            title (str): Title of the dialog
            win_cont (QWidget): Parent Qt dialog.
            icon (QIcon): Window icon.
            data (MaterialsCoverageData): The material data.
            edit_sediment (bool): flag to allow editing sediment properties.
        """
        super().__init__(win_cont)
        self.parent = win_cont
        self.icon = icon
        self.help_url = 'https://www.xmswiki.com/wiki/SMS:Display_Options'
        self.widgets = {}

        self.material_data = data

        # Setup the dialog
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)
        self.setup_ui()
        self.adjustSize()

        # Calculate a reasonable width for the dialog.
        self.dlg_width = self.widgets['table_view'].table_view.horizontalHeader().length()
        self.dlg_width += self.widgets['table_view'].style().pixelMetric(QStyle.PM_ScrollBarExtent) * 3
        self.dlg_width += self.widgets['table_view'].table_view.frameWidth() * 2
        self.dlg_width += 20
        self.resize(self.dlg_width, self.size().height())

    def setup_ui(self):
        """Setup dialog widgets."""
        # Add a main vertical layout.
        self.widgets['main_vert_layout'] = QVBoxLayout()
        self.setLayout(self.widgets['main_vert_layout'])

        # set up the materials table view
        self._setup_ui_materials_view()

        # add the ok, cancel, help... buttons at the bottom of the dialog
        self._setup_ui_bottom_button_box()

    def _setup_ui_materials_view(self):
        """Sets up the table view for the materials."""
        self.widgets['table_view'] = MaterialTableWidget(self, self.material_data.coverage_data.to_dataframe())
        self.widgets['main_vert_layout'].addWidget(self.widgets['table_view'])

    def _setup_ui_bottom_button_box(self):
        """Add buttons to the bottom of the dialog."""
        # Add Import and Export buttons
        self.widgets['btn_horiz_layout'] = QHBoxLayout()

        self.widgets['btn_box'] = QDialogButtonBox()
        self.widgets['btn_box'].setOrientation(Qt.Horizontal)
        self.widgets['btn_box'].setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.Help
        )
        self.widgets['btn_box'].accepted.connect(self.accept)
        self.widgets['btn_box'].rejected.connect(self.reject)
        self.widgets['btn_box'].helpRequested.connect(self.help_requested)
        self.widgets['btn_horiz_layout'].addWidget(self.widgets['btn_box'])

        self.widgets['main_vert_layout'].addLayout(self.widgets['btn_horiz_layout'])

    def help_requested(self):  # pragma: no cover
        """Called when the Help button is clicked."""
        webbrowser.open(self.help_url)

    def accept(self):
        """Save material properties."""
        self.material_data.coverage_data = self.widgets['table_view'].model.data_frame.to_xarray()
        self.material_data.commit()
        super().accept()
