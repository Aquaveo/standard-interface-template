"""Coverage component class."""
# 1. Standard python modules
import os
import shutil

# 2. Third party modules
import pandas as pd
import xarray as xr

# 3. Aquaveo modules
from xmsapi.dmi import ActionRequest, DialogModality
from xmscomponents.display.display_options_io import (read_display_option_ids, read_display_options_from_json,
                                                      write_display_option_ids, write_display_options_to_json)
from xmscomponents.display.xms_display_message import DrawType, XmsDisplayMessage
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList
from xmsguipy.data.target_type import TargetType
from xmsguipy.dialogs.category_display_options_list import CategoryDisplayOptionsDialog

# 4. Local modules
from standard_interface_template.components.standard_base_component import StandardBaseComponent
from standard_interface_template.data.boundary_coverage_data import BoundaryCoverageData
from standard_interface_template.gui.boundary_dialog import BoundaryDialog


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


COVERAGE_INITIAL_ATT_ID_FILE = 'initial_coverage.attids'
COVERAGE_INITIAL_COMP_ID_FILE = 'initial_coverage.compids'


class BoundaryCoverageComponent(StandardBaseComponent):
    """A hidden Dynamic Model Interface (DMI) component for the Standard Interface Template model simulation."""

    def __init__(self, main_file):
        """Initializes the data class.

        Args:
            main_file: The main file associated with this component.
        """
        super().__init__(main_file)
        self.data = BoundaryCoverageData(main_file)
        self.class_name = 'BoundaryCoverageComponent'
        self.module_name = 'standard_interface_template.components.boundary_coverage_component'
        #                    [(menu_text, menu_method)...]
        self.tree_commands = [
            ('Display Options...', 'open_display_options'),
        ]
        self.arc_commands = [
            ('Assign Arc', 'open_assign_arc'),
        ]
        self.point_commands = [
            ('Assign Point', 'open_assign_point'),
        ]
        self.disp_opts_file = os.path.join(os.path.dirname(self.main_file), 'boundary_coverage_display_options.json')
        if not os.path.isfile(self.main_file):
            # Read the default display options, and save ourselves a copy with a randomized UUID.
            categories = CategoryDisplayOptionList()  # Generates a random UUID key for the display list
            default_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                        'gui', 'resources', 'default_data',
                                        'default_boundary_coverage_display_options.json')
            json_dict = read_display_options_from_json(default_file)
            json_dict['comp_uuid'] = os.path.basename(os.path.dirname(self.main_file))
            categories.from_dict(json_dict)
            write_display_options_to_json(self.disp_opts_file, categories)
            # Save our display list UUID to the main file
            self.data.info.attrs['display_uuid'] = categories.uuid
            self.data.commit()
        else:
            self.cov_uuid = self.data.info.attrs['cov_uuid']

    def save_to_location(self, new_path, save_type):
        """Save component files to a new location.

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
            json_dict = self.duplicate_display_opts(new_path, os.path.basename(self.disp_opts_file))
            data = BoundaryCoverageData(new_main_file)
            data.load_all()
            data.info.attrs['cov_uuid'] = ''
            data.info.attrs['display_uuid'] = json_dict['uuid']
            data.commit()

        return new_main_file, messages, action_requests

    def create_event(self, lock_state):
        """This will be called when the component is created from nothing.

        Args:
            lock_state (bool): True if the the component is locked for editing. Do not change the files if locked.

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.

        """
        self.data.commit()
        id_dir = os.path.join(os.path.dirname(self.main_file), 'display_ids')
        os.mkdir(id_dir)

        action = ActionRequest()
        action.SetDialogModality(DialogModality.NO_DIALOG)
        action.SetMethodAction('get_initial_display_options')
        action.SetClass(self.class_name)
        action.SetModule(self.module_name)
        action.SetMainFile(self.main_file)

        messages = []
        action_requests = [action]
        return messages, action_requests

    def get_initial_display_options(self, query, params):
        """Get the coverage UUID from XMS and send back the display options list.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            params (:obj:`dict'): Generic map of parameters. Unused in this case.

        Returns:
            Empty message and ActionRequest lists

        """
        query.select('Parent')  # Go up to the parent coverage.
        uuid_result = query.get('geom_guid')['geom_guid']
        if not uuid_result or not uuid_result[0]:
            return [('ERROR', 'Could not get Standard Interface coverage UUID.')], []
        self.cov_uuid = uuid_result[0].get_as_string()

        initial_att_file = os.path.join(os.path.dirname(self.main_file), COVERAGE_INITIAL_ATT_ID_FILE)
        if os.path.isfile(initial_att_file):  # Came from a model native read, initialize the component ids.
            att_ids = read_display_option_ids(initial_att_file)
            initial_comp_file = os.path.join(os.path.dirname(self.main_file), COVERAGE_INITIAL_COMP_ID_FILE)
            comp_ids = read_display_option_ids(initial_comp_file)
            os.remove(initial_att_file)
            os.remove(initial_comp_file)
            for att_id, comp_id in zip(att_ids, comp_ids):
                self.update_component_id(TargetType.arc, att_id, comp_id)

        self.data.info.attrs['cov_uuid'] = self.cov_uuid
        self.data.commit()
        # Send the display message to XMS.
        self.display_option_list.append(
            XmsDisplayMessage(file=self.disp_opts_file, edit_uuid=self.cov_uuid)
        )
        return [], []

    def open_assign_arc(self, query, params, win_cont, icon):
        """Opens the Assign Arc dialog and saves component data state on OK.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            params (:obj:`dict'): Generic map of parameters. Contains selection map and component id files.
            win_cont (:obj:`PySide2.QtWidgets.QWidget`): The window container.
            icon (:obj:`PySide2.QtGui.QIcon`): Icon to show in the dialog title

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.

        """
        arc_ids = []
        params = {key.get_as_string(): value for key, value in params[0].items()}
        if 'selection' in params:
            arc_ids = [arc_id.get_as_int() for arc_id in params['selection']]
        num_arcs = len(arc_ids)
        if num_arcs == 0:
            return [('INFO', 'No arcs selected. Select one or more arcs to assign properties.')], []

        # Get the component id map of the selected (if any).
        comp_id = -1
        if 'id_files' in params:
            if params['id_files'] and params['id_files'][0]:
                files_dict = {
                    'ARC': (params['id_files'][0].get_as_string(), params['id_files'][1].get_as_string())
                }
                self.load_coverage_component_id_map(files_dict)
                target_type = TargetType.arc
                try:
                    selected_comp_ids = list(self.comp_to_xms[self.cov_uuid][target_type].keys())
                    comp_id = selected_comp_ids[0] if selected_comp_ids else -1
                except KeyError:
                    comp_id = -1  # No component ids assigned for any of the selected arcs
        single_arc = self.data.coverage_data.where(self.data.coverage_data.comp_id == comp_id, drop=True)
        if single_arc.user_option.size == 0:
            # Here we are using component id 0 for default values.
            single_arc = self.data.coverage_data.where(self.data.coverage_data.comp_id == 0, drop=True)
        dialog = BoundaryDialog(win_cont, icon, 'Arc Dialog', single_arc.user_text.item(0),
                                single_arc.user_option.item(0))
        if dialog.exec():
            dlg_data = dialog.get_dialog_data_dict()
            edit = dlg_data['user_edit']
            option = dlg_data['user_display']
            new_comp_id = int(self.data.coverage_data.comp_id.max() + 1)
            new_values = []
            for arc_id in arc_ids:
                self.update_component_id(TargetType.arc, arc_id, new_comp_id)
                new_values.append([new_comp_id, option, edit])
                new_comp_id += 1
            values_dataset = pd.DataFrame(new_values, columns=['comp_id', 'user_option', 'user_text']).to_xarray()
            self.data.coverage_data = xr.concat([self.data.coverage_data, values_dataset], 'index')
            self.update_id_files()
            self.display_option_list.append(
                XmsDisplayMessage(file=self.disp_opts_file, edit_uuid=self.cov_uuid)
            )
            self.data.commit()

        # Delete the id dumped by xms files.
        shutil.rmtree(os.path.join(os.path.dirname(self.main_file), 'temp'), ignore_errors=True)

        return [], []

    def open_assign_point(self, query, params, win_cont, icon):
        """Opens the Assign Point dialog and saves component data state on OK.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            params (:obj:`dict'): Generic map of parameters. Contains selection map and component id files.
            win_cont (:obj:`PySide2.QtWidgets.QWidget`): The window container.
            icon (:obj:`PySide2.QtGui.QIcon`): Icon to show in the dialog title

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.

        """
        point_ids = []
        params = {key.get_as_string(): value for key, value in params[0].items()}
        if 'selection' in params:
            point_ids = [point_id.get_as_int() for point_id in params['selection']]
        num_arcs = len(point_ids)
        if num_arcs == 0:
            return [('INFO', 'No points selected. Select one or more points to assign properties.')], []

        # Get the component id map of the selected (if any).
        comp_id = -1
        if 'id_files' in params:
            if params['id_files'] and params['id_files'][0]:
                files_dict = {
                    'POINT': (params['id_files'][0].get_as_string(), params['id_files'][1].get_as_string())
                }
                self.load_coverage_component_id_map(files_dict)
                target_type = TargetType.point
                try:
                    selected_comp_ids = list(self.comp_to_xms[self.cov_uuid][target_type].keys())
                    comp_id = selected_comp_ids[0] if selected_comp_ids else -1
                except KeyError:
                    comp_id = -1  # No component ids assigned for any of the selected points
        single_point = self.data.coverage_data.where(self.data.coverage_data.comp_id == comp_id, drop=True)
        if single_point.user_option.size == 0:
            # Here we are using component id 0 for default values.
            single_point = self.data.coverage_data.where(self.data.coverage_data.comp_id == 0, drop=True)
        dialog = BoundaryDialog(win_cont, icon, 'Point Dialog', single_point.user_text.item(0),
                                single_point.user_option.item(0))
        if dialog.exec():
            dlg_data = dialog.get_dialog_data_dict()
            edit = dlg_data['user_edit']
            option = dlg_data['user_display']
            new_comp_id = int(self.data.coverage_data.comp_id.max() + 1)
            new_values = []
            for point_id in point_ids:
                self.update_component_id(TargetType.point, point_id, new_comp_id)
                new_values.append([new_comp_id, option, edit])
                new_comp_id += 1
            values_dataset = pd.DataFrame(new_values, columns=['comp_id', 'user_option', 'user_text']).to_xarray()
            self.data.coverage_data = xr.concat([self.data.coverage_data, values_dataset], 'index')
            self.update_id_files()
            self.display_option_list.append(
                XmsDisplayMessage(file=self.disp_opts_file, edit_uuid=self.cov_uuid)
            )
            self.data.commit()

        # Delete the id dumped by xms files.
        shutil.rmtree(os.path.join(os.path.dirname(self.main_file), 'temp'), ignore_errors=True)

        return [], []

    def open_display_options(self, query, params, win_cont, icon):
        """Shows the display options dialog.

        Args:
            query (:obj:'xmsapi.dmi.Query'):
            params (:obj:'list' of :obj:'str'):
            win_cont (:obj:'PySide2.QtWidgets.QWidget'): The window container.
            icon (:obj:'PySide2.QtGui.QIcon'): Icon to show in the dialog title

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
                    XmsDisplayMessage(
                        file=self.disp_opts_file, edit_uuid=self.cov_uuid,
                    )
                )
                break  # only one list
        return [], []

    def update_id_files(self):
        """Writes the display id files."""
        df = self.data.coverage_data.to_dataframe()
        disp_names = BoundaryCoverageData.display_list
        for i in range(len(disp_names)):
            self._write_id_file(disp_names[i], df)

    def _write_id_file(self, disp_name, df):
        """Write a single id file.

        Args:
            disp_name (str):
            df (DataFrame):
        """
        df1 = df.loc[df['user_option'] == disp_name]
        ids = df1['comp_id'].astype(dtype='i4').to_list()
        id_file = os.path.join(os.path.dirname(self.main_file), f'display_ids/{disp_name}.display_ids')
        write_display_option_ids(id_file, ids)
