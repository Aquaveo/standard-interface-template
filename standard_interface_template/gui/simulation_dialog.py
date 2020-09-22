"""A dialog class."""
# 1. Standard python modules
import webbrowser

# 2. Third party modules
from PySide2.QtCore import Qt

# 3. Aquaveo modules
from xmsguipy.dialogs.xms_parent_dlg import XmsDlg

# 4. Local modules
from standard_interface_template.gui.simulation_dialog_ui import Ui_SimulationDialog


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationDialog(XmsDlg):
    """A dialog for assigning values."""

    def __init__(self, win_cont, icon, title, user_text, user_option):
        """
        Initializes the class, sets up the ui, and writes the values.

        Args:
            win_cont (:obj:`QWidget`): Parent window.
            icon (:obj:`QIcon`): Window icon.
            title (str): Window title.
            user_text (str): The user editable text for the dialog.
            user_option (str): The user editable current option.
        """
        super().__init__(win_cont, 'standard_interface_template.gui.simulation_dialog')
        self.help_url = 'https://www.xmswiki.com/wiki/SMS:Display_Options'

        # This is how you get a python file from a *.ui file. Run this after every edit to the *.ui file.
        # <path-to-python/Scripts>pyside2-uic <ui-file-name>.ui > <ui-file-name>_ui.py

        # If a *.ui file is used, the class created from the *.ui file needs to be setup.
        self.ui = Ui_SimulationDialog()
        self.ui.setupUi(self)

        self.ui.user_type.addItems(['A', 'B', 'C'])

        self.ui.user_edit.setText(user_text)
        self.ui.user_type.setCurrentText(user_option)

        # Set the window flags and the window icon and the window title.
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)
        self.adjustSize()

        self.ui.button_box.helpRequested.connect(self.help_requested)

    def help_requested(self):
        """Called when the Help button is clicked."""
        webbrowser.open(self.help_url)

    def get_dialog_data_dict(self):
        """Returns a dict of the dialog input widget values."""
        return {
            'user_type': self.ui.user_type.currentText(),
            'user_edit': self.ui.user_edit.text(),
        }
