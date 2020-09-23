"""BoundaryMappedComponent class. Data mapped from a BC Coverage onto an Standard Interface mesh."""
# 1. Standard python modules
import os

# 2. Third party modules

# 3. Aquaveo modules
from xmscomponents.display.display_options_io import read_display_options_from_json, write_display_options_to_json
from xmscomponents.display.xms_display_message import DrawType, XmsDisplayMessage
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList
from xmsguipy.dialogs.category_display_options_list import CategoryDisplayOptionsDialog

# 4. Local modules
from standard_interface_template.components.materials_mapped_component import MaterialsMappedComponent


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class BoundaryMappedComponent(MaterialsMappedComponent):
    """A Dynamic Model Interface (DMI) component for the Standard Interface model snap preview."""

    def __init__(self, main_file):
        """
        Initializes the base component class.

        Args:
            main_file: The main file associated with this component.
        """
        super().__init__(main_file)
        self.class_name = 'BoundaryMappedComponent'
        self.module_name = 'standard_interface_template.components.boundary_mapped_component'
        # [(menu_text, menu_method)...]
        self.tree_commands = [
            ('Display Options...', 'open_display_options'),
        ]
        self.disp_opts_file = os.path.join(os.path.dirname(self.main_file), 'boundary_coverage_display_options.json')

    def save_to_location(self, new_path, save_type):
        """
        Save component files to a new location.

        Args:
            new_path (str): Path to the new save location.
            save_type (str): One of DUPLICATE, PACKAGE, SAVE, SAVE_AS, LOCK.
                DUPLICATE happens when the tree item owner is duplicated. The new component will always be unlocked to
                start with.
                PACKAGE happens when the project is being saved as a package. As such, all data must be copied and all
                data must use relative file paths.
                SAVE happens when re-saving this project.
                SAVE_AS happens when saving a project in a new location. This happens the first time we save a project.
                UNLOCK happens when the component is about to be changed and it does not have a matching uuid folder in
                the temp area. May happen on project read if the XML specifies to unlock by default.

        Returns:
            (:obj:`tuple`): tuple containing:
                - new_main_file (str): Name of the new main file relative to new_path, or an absolute path if necessary.
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        new_main_file, messages, action_requests = super().save_to_location(new_path, save_type)

        if save_type == 'DUPLICATE':
            json_dict = self.duplicate_display_opts(new_path, 'boundary_coverage_display_options.json')
            self.update_display_options(new_main_file, json_dict, action_requests)

        return new_main_file, messages, action_requests

    def open_display_options(self, query, params, win_cont, icon):
        """
        Shows the display options dialog.

        Args:
            query (:obj:`xmsapi.dmi.Query`): An object for communicating with XMS. Unused by this method.
            params (:obj:`list` of :obj:`str`): A list of parameters add to the ActionRequest. Unused by this method.
            win_cont (:obj:`PySide2.QtWidgets.QWidget`): The window container.
            icon (:obj:`PySide2.QtGui.QIcon`): Icon to show in the dialog title.

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        categories = CategoryDisplayOptionList()
        json_dict = read_display_options_from_json(self.disp_opts_file)
        categories.from_dict(json_dict)
        categories_list = [categories]

        dlg = CategoryDisplayOptionsDialog(categories_list, win_cont)
        dlg.setWindowIcon(icon)
        dlg.setModal(True)
        if dlg.exec():
            # write files
            category_lists = dlg.get_category_lists()
            for category_list in category_lists:
                write_display_options_to_json(self.disp_opts_file, category_list)
                self.display_option_list.append(
                    XmsDisplayMessage(file=self.disp_opts_file, draw_type=DrawType.draw_at_locations)
                )
                break  # only one list
        return [], []
