"""For testing."""

# 1. Standard python libraries
import os
import shutil
import sys
import unittest

# 2. Third party libraries
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QApplication, QCheckBox, QLabel, QLineEdit

# 3. Aquaveo libraries
from xmsguipy.testing.gui_test_helper import GuiTestHelper

# 4. Local libraries
from standard_interface_template.data.materials_coverage_data import MaterialsCoverageData
from standard_interface_template.gui.materials_dialog import MaterialsDialog

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsDialogGuiTests(unittest.TestCase):
    """
    Tests the MaterialsDialog class.
    """

    @classmethod
    def setUpClass(cls):
        """Sets up the current working directory for all tests in the class. Also ensures a QApplication exists."""
        # Change working directory to test location
        os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

    def setUp(self):
        """Create sediment constituents data for use in the tests."""
        self.dlg = None

    def test_added_material_default(self):
        """Tests dependencies in the material widget starting from default."""
        out_file = 'does_not_exist.nc'
        if os.path.exists(out_file):
            shutil.rmtree(out_file)
        mat_data = MaterialsCoverageData(out_file)
        icon = QIcon()
        self.dlg = MaterialsDialog('Material List and Properties', None, icon,  mat_data)
        self.dlg.show()

        add_action = self.dlg.widgets['table_view'].btn_actions[self.dlg.widgets['table_view'].add_icon]
        add_button = self.dlg.widgets['table_view'].toolbar.widgetForAction(add_action)
        delete_action = self.dlg.widgets['table_view'].btn_actions[self.dlg.widgets['table_view'].delete_icon]
        delete_button = self.dlg.widgets['table_view'].toolbar.widgetForAction(delete_action)

        self.assertFalse(delete_button.isEnabled())

        QTest.mouseClick(add_button, Qt.MouseButton.LeftButton)
        GuiTestHelper.process_events()

        self.assertEqual(self.dlg.widgets['table_view'].model.rowCount(), 2)
        self.assertTrue(delete_button.isEnabled())

        self.dlg.close()
