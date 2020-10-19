"""Base class for components class."""
# 1. Standard python modules
from distutils.dir_util import copy_tree
import os
import shutil
import uuid

# 2. Third party modules

# 3. Aquaveo modules
from xmsapi.dmi import ActionRequest, DialogModality, MenuItem
from xmscomponents.bases.coverage_component_base import CoverageComponentBase
from xmscomponents.display.display_options_io import read_display_options_from_json, write_display_options_to_json
from xmscomponents.display.xms_display_message import DrawType, XmsDisplayMessage
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList

# 4. Local modules


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class StandardBaseComponent(CoverageComponentBase):
    """A Dynamic Model Interface (DMI) component base for the Standard Interface Template model."""

    def __init__(self, main_file):
        """
        Initializes the data class.

        Args:
            main_file (str): The main file associated with this component.
        """
        super().__init__(main_file.strip('"\''))
        self.data = None
        self.class_name = ''
        self.module_name = ''
        self.tree_commands = []  # [(menu_text, menu_method)...]
        self.polygon_commands = []  # [(menu_text, menu_method)...]
        self.arc_commands = []  # [(menu_text, menu_method)...]
        self.point_commands = []  # [(menu_text, menu_method)...]
        self.uuid = os.path.basename(os.path.dirname(self.main_file))
        self.disp_opts_file = ''
        self.cov_uuid = ''

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
        messages = []
        action_requests = []

        # Check if we are already in the new location
        new_main_file = os.path.join(new_path, os.path.basename(self.main_file))
        if os.path.normcase(new_main_file) == os.path.normcase(self.main_file):
            return self.main_file, [], []

        copy_tree(os.path.dirname(self.main_file), os.path.dirname(new_main_file))

        return new_main_file, messages, action_requests

    def project_open_event(self, new_path):
        """
        Called when an XMS project is opened.

        Components with display lists should add XmsDisplayMessage(s) to self.display_option_list.

        Args:
            new_path (str): Path to the new save location.
        """
        if self.disp_opts_file:  # Component has a display list
            new_disp_opts = os.path.join(new_path, os.path.basename(self.disp_opts_file))
            if self.cov_uuid:  # drawing on a coverage by id
                self.display_option_list.append(
                    XmsDisplayMessage(file=new_disp_opts, edit_uuid=self.cov_uuid)
                )
            else:  # Free location draw of a mapped component
                self.display_option_list.append(
                    XmsDisplayMessage(file=new_disp_opts, draw_type=DrawType.draw_at_locations)
                )

    def get_project_explorer_menus(self, main_file_list):
        """
        This will be called when right-click menus in the project explorer area of XMS are being created.

        Args:
            main_file_list (:obj:`list` of str): A list of the main files of the selected components of this type.

        Returns:
            menu_items (:obj:`list` of :obj:`xmsapi.dmi.MenuItem`): A list of menus and menu items to be shown. Note
                that this list can have objects of type xmsapi.dmi.Menu as well as xmsapi.dmi.MenuItem. "None" may be
                added to the list to indicate a separator.
        """
        if len(main_file_list) > 1 or not main_file_list or not self.tree_commands:
            return []  # Multi-select, nothing selected, or no project explorer menu commands for this component

        menu_list = [None]  # None == spacer
        # Add all the project explorer menus
        for command_text, command_method in self.tree_commands:
            menu_item = MenuItem()
            menu_item.SetText(command_text)
            action = ActionRequest()
            action.SetDialogModality(DialogModality.MODAL)
            action.SetMethodAction(command_method)
            action.SetClass(self.class_name)
            action.SetModule(self.module_name)
            action.SetMainFile(main_file_list[0][0])
            menu_item.SetActionRequest(action)
            menu_list.append(menu_item)

        return menu_list

    def get_display_menus(self, selection, lock_state, id_files):
        """
        This will be called when right-click menus in the main display area of XMS are being created.

        Args:
            selection (dict): A dictionary with the key being a string of the feature entity type (POINT, ARC, POLYGON).
                The value of the dictionary is a list of IntegerLiteral ids of the selected feature objects.
            lock_state (bool): True if the the component is locked for editing. Do not change the files if locked.
            id_files (:obj:`dict`): Key is entity type string, value is tuple of two str where first is the file
                location of the XMS coverage id binary file. Second is file location of the component coverage id binary
                file. Only applicable for coverage selections. File will be deleted after event. Copy if need to
                persist.

        Returns:
            menu_items (:obj:`list` of :obj:`xmsapi.dmi.MenuItem`): A list of menus and menu items to be shown. Note
                that this list can have objects of type xmsapi.dmi.Menu as well as xmsapi.dmi.MenuItem. "None" may be
                added to the list to indicate a separator.
        """
        menu_list = [None]  # None == spacer
        # Copy all the id files to a temporary location. XMS will delete them once this method returns.
        temp_dir = os.path.join(os.path.dirname(self.main_file), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        unpacked_id_files = {}
        for entity, filenames in id_files.items():
            if not os.path.exists(filenames[0]) or not os.path.exists(filenames[1]):
                id_files[entity] = ('', '')
                continue
            temp_xms_file = os.path.join(temp_dir, os.path.basename(filenames[0]))
            temp_comp_file = os.path.join(temp_dir, os.path.basename(filenames[1]))
            shutil.copyfile(filenames[0], temp_xms_file)
            shutil.copyfile(filenames[1], temp_comp_file)
            unpacked_id_files[entity] = (temp_xms_file, temp_comp_file)

        if 'POLYGON' in selection:
            poly_id_files = unpacked_id_files['POLYGON'] if 'POLYGON' in unpacked_id_files else None
            for command_text, command_method in self.polygon_commands:
                menu_item = MenuItem()
                menu_item.SetText(command_text)
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': poly_id_files, 'selection': selection['POLYGON']})
                menu_item.SetActionRequest(action)
                menu_list.append(menu_item)
        if 'ARC' in selection:
            arc_id_files = unpacked_id_files['ARC'] if 'ARC' in unpacked_id_files else None
            for command_text, command_method in self.arc_commands:
                menu_item = MenuItem()
                menu_item.SetText(command_text)
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': arc_id_files, 'selection': selection['ARC']})
                menu_item.SetActionRequest(action)
                menu_list.append(menu_item)
        if 'POINT' in selection:
            point_id_files = unpacked_id_files['POINT'] if 'POINT' in unpacked_id_files else None
            for command_text, command_method in self.point_commands:
                menu_item = MenuItem()
                menu_item.SetText(command_text)
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': point_id_files, 'selection': selection['POINT']})
                menu_item.SetActionRequest(action)
                menu_list.append(menu_item)
        if not menu_list:
            shutil.rmtree(temp_dir, ignore_errors=True)  # Delete the id files if no menus were added.
        return menu_list

    def get_double_click_actions_for_selection(self, selection, lock_state, id_files):
        """
        This will be called when a double-click in the main display area of XMS happened.

        Args:
            selection (dict): A dictionary with the key being a string of the feature entity type (POINT, ARC, POLYGON).
                The value of the dictionary is a list of IntegerLiteral ids of the selected feature objects.
            lock_state (bool): True if the the component is locked for editing. Do not change the files if locked.
            id_files (:obj:`dict`): Key is entity type string, value is tuple of two str where first is the file
                location of the XMS coverage id binary file. Second is file location of the component coverage id binary
                file. Only applicable for coverage selections. File will be deleted after event. Copy if need to
                persist.

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        # Copy all the id files to a temporary location. XMS will delete them once this method returns.
        temp_dir = os.path.join(os.path.dirname(self.main_file), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        unpacked_id_files = {}
        for entity, filenames in id_files.items():
            if not os.path.exists(filenames[0]) or not os.path.exists(filenames[1]):
                id_files[entity] = ('', '')
                continue
            temp_xms_file = os.path.join(temp_dir, os.path.basename(filenames[0]))
            temp_comp_file = os.path.join(temp_dir, os.path.basename(filenames[1]))
            shutil.copyfile(filenames[0], temp_xms_file)
            shutil.copyfile(filenames[1], temp_comp_file)
            unpacked_id_files[entity] = (temp_xms_file, temp_comp_file)

        actions = []
        if 'POLYGON' in selection:
            poly_id_files = unpacked_id_files['POLYGON'] if 'POLYGON' in unpacked_id_files else None
            for _, command_method in self.polygon_commands:
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': poly_id_files, 'selection': selection['POLYGON']})
                actions.append(action)
                break  # Only expecting one dialog ActionRequest on double-click
        if 'ARC' in selection:
            arc_id_files = unpacked_id_files['ARC'] if 'ARC' in unpacked_id_files else None
            for _, command_method in self.arc_commands:
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': arc_id_files, 'selection': selection['ARC']})
                actions.append(action)
                break  # Only expecting one dialog ActionRequest on double-click
        if 'POINT' in selection:
            point_id_files = unpacked_id_files['POINT'] if 'POINT' in unpacked_id_files else None
            for _, command_method in self.point_commands:
                action = ActionRequest()
                action.SetDialogModality(DialogModality.MODAL)
                action.SetMethodAction(command_method)
                action.SetClass(self.class_name)
                action.SetModule(self.module_name)
                action.SetMainFile(self.main_file)
                action.SetActionParameterItems({'id_files': point_id_files, 'selection': selection['POINT']})
                actions.append(action)
                break
        if not actions:
            shutil.rmtree(temp_dir, ignore_errors=True)  # Delete the id files if no menus were added.
        return [], actions

    def query_for_all_component_ids(self, query, target_type, cleanup=True):
        """
        Query XMS for a dump of all the current component ids of the specified entity type.

        Query needs to be at the Component Context level (or any
        other node with a "ComponentCoverageIds" ContextDefinition out edge).

        Args:
            query (:obj:`xmsdmi.dmi.Query`): Query for communicating with XMS.
            target_type (:obj:`xmsguipy.data.target_type.TargetType`): Entity type enum.
            cleanup (bool): True if id files should be deleted after loading.

        Returns:
            (dict): Key is stringified entity type and value is tuple of xms and component id files.
        """
        start_ctxt = query.get_context()
        query.select('ComponentCoverageIds')
        cov_uuid = self.data.info.attrs['cov_uuid']
        keyword = f'{self.uuid}#{cov_uuid}#{int(target_type)}'
        id_res = query.get(keyword)[keyword]
        file_dict = {
            key.get_as_string(): (value[0].get_as_string(), value[1].get_as_string())
            for key, value in id_res[0][0].items()
        }
        self.load_coverage_component_id_map(file_dict)
        if cleanup:
            for _, val in file_dict.items():
                for f in val:
                    if os.path.exists(f):
                        os.remove(f)
        query.set_context(start_ctxt)
        return file_dict

    @staticmethod
    def duplicate_display_opts(new_path, disp_opts_fname):
        """
        Duplicates display options.

        Args:
            new_path (str): Path to the new save location.
            disp_opts_fname (str): The filename (no path) of the display options JSON file.

        Returns:
            (json_dict): dict containing the display options.
        """
        fname = os.path.join(new_path, disp_opts_fname)
        json_dict = read_display_options_from_json(fname)
        if 'uuid' in json_dict:
            json_dict['uuid'] = str(uuid.uuid4())
            json_dict['comp_uuid'] = os.path.basename(new_path)
            categories = CategoryDisplayOptionList()  # Generates a random UUID key for the display list
            categories.from_dict(json_dict)
            write_display_options_to_json(fname, categories)
        return json_dict
