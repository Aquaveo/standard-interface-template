"""MaterialsMappedComponent class. Data from a material coverage mapped to Standard Interface mesh."""
# 1. Standard python modules
import os

# 2. Third party modules

# 3. Aquaveo modules
from xmsapi.dmi import ActionRequest, DialogModality
from xmscomponents.display.xms_display_message import DrawType, XmsDisplayMessage

# 4. Local modules
from standard_interface_template.components.standard_base_component import StandardBaseComponent


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialsMappedComponent(StandardBaseComponent):
    """A Dynamic Model Interface (DMI) component for the Standard Interface model snap preview."""

    def __init__(self, main_file):
        """
        Initializes the base component class.

        Args:
            main_file (str): The main file associated with this component.
        """
        super().__init__(main_file)
        self.class_name = 'MaterialsMappedComponent'
        self.module_name = 'standard_interface_template.components.materials_mapped_component'
        self.disp_opts_file = os.path.join(os.path.dirname(self.main_file), 'material_display_options.json')

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
            json_dict = self.duplicate_display_opts(new_path, 'material_display_options.json')
            self.update_display_options(new_main_file, json_dict, action_requests)

        return new_main_file, messages, action_requests

    def create_event(self, lock_state):
        """
        This will be called when the component is created from nothing.

        Args:
            lock_state (bool): True if the the component is locked for editing. Do not change the files if locked.

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        action = self.get_display_options_action()

        messages = []
        action_requests = [action]
        return messages, action_requests

    def get_initial_display_options(self, query, params):
        """
        Get the coverage UUID from XMS and send back the display options list.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
            params (:obj:`dict`): Generic map of parameters. Unused in this case.

        Returns:
            Empty message and ActionRequest lists.
        """
        # Send the default display options list to XMS.
        self.display_option_list.append(
            XmsDisplayMessage(file=self.main_file, draw_type=DrawType.draw_at_locations)
        )
        return [], []

    def get_display_options_action(self):
        """Get an ActionRequest that will refresh the XMS display list for components with display."""
        action = ActionRequest()
        action.SetDialogModality(DialogModality.NO_DIALOG)
        action.SetMethodAction('get_initial_display_options')
        action.SetClass(self.class_name)
        action.SetModule(self.module_name)
        action.SetMainFile(self.main_file)
        return action

    def update_display_options(self, new_main_file, json_dict, action_requests):
        """
        Update the display options.

        Args:
            new_main_file (str): file name.
            json_dict (dict): display options dictionary.
            action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        if 'comp_uuid' in json_dict:
            action = self.get_display_options_action()
            action.SetMainFile(new_main_file)
            action.set_component_uuid(json_dict['comp_uuid'])
            action_requests.append(action)
