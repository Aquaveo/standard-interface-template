"""Coverage component class."""
# 1. Standard python modules
import os
import shutil

# 2. Third party modules
import pandas as pd
from PySide2.QtGui import QColor
import xarray as xr

# 3. Aquaveo modules
from xmsapi.dmi import ActionRequest, DialogModality
from xmscomponents.display.display_options_io import (read_display_option_ids, read_display_options_from_json,
                                                      write_display_option_ids, write_display_options_to_json)
from xmscomponents.display.xms_display_message import DrawType, XmsDisplayMessage
from xmsguipy.data.category_display_option import CategoryDisplayOption
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList
from xmsguipy.data.polygon_texture import PolygonOptions, PolygonTexture
from xmsguipy.data.target_type import TargetType
from xmsguipy.dialogs.category_display_options_list import CategoryDisplayOptionsDialog

# 4. Local modules
from standard_interface_template.components.standard_base_component import StandardBaseComponent
from standard_interface_template.data.materials_coverage_data import MaterialsCoverageData
from standard_interface_template.gui.assign_poly_material_dialog import AssignPolyMaterialDialog
from standard_interface_template.gui.materials_dialog import MaterialDialog


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


MAT_COVERAGE_INITIAL_ATT_ID_FILE = 'initial_coverage.attids'
MAT_COVERAGE_INITIAL_COMP_ID_FILE = 'initial_coverage.compids'


class MaterialsCoverageComponent(StandardBaseComponent):
    """A hidden Dynamic Model Interface (DMI) component for the Standard Interface Template model simulation."""

    def __init__(self, main_file):
        """Initializes the data class.

        Args:
            main_file: The main file associated with this component.
        """
        super().__init__(main_file)
        self.data = MaterialsCoverageData(main_file)
        self.class_name = 'MaterialsCoverageComponent'
        self.module_name = 'standard_interface_template.components.materials_coverage_component'
        #                    [(menu_text, menu_method)...]
        self.tree_commands = [
            ('Materials...', 'open_materials'),
        ]
        self.polygon_commands = [
            ('Assign Polygon', 'open_assign_polygon'),
        ]
        self.disp_opts_file = os.path.join(os.path.dirname(self.main_file), 'materials_coverage_display_options.json')
        if not os.path.isfile(self.main_file):
            # Read the default display options, and save ourselves a copy with a randomized UUID.
            categories = CategoryDisplayOptionList()  # Generates a random UUID key for the display list
            default_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                        'gui', 'resources', 'default_data',
                                        'default_materials_coverage_display_options.json')
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
            data = MaterialsCoverageData(new_main_file)
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

        initial_att_file = os.path.join(os.path.dirname(self.main_file), MAT_COVERAGE_INITIAL_ATT_ID_FILE)
        if os.path.isfile(initial_att_file):  # Came from a model native read, initialize the component ids.
            att_ids = read_display_option_ids(initial_att_file)
            initial_comp_file = os.path.join(os.path.dirname(self.main_file), MAT_COVERAGE_INITIAL_COMP_ID_FILE)
            comp_ids = read_display_option_ids(initial_comp_file)
            os.remove(initial_att_file)
            os.remove(initial_comp_file)
            for att_id, comp_id in zip(att_ids, comp_ids):
                self.update_component_id(TargetType.polygon, att_id, comp_id)
            id_dir = os.path.join(os.path.dirname(self.main_file), 'display_ids')
            os.mkdir(id_dir)
            categories = self._get_category_list()
            write_display_options_to_json(self.disp_opts_file, categories)
            self.update_display_id_files([], list(self.data.coverage_data.material_id.values))

        self.data.info.attrs['cov_uuid'] = self.cov_uuid
        self.data.commit()
        # Send the display message to XMS.
        self.display_option_list.append(
            XmsDisplayMessage(file=self.disp_opts_file, edit_uuid=self.cov_uuid)
        )
        return [], []

    def open_assign_polygon(self, query, params, win_cont, icon):
        """Opens the Assign Polygon dialog and saves component data state on OK.

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
        polygon_ids = []
        params = {key.get_as_string(): value for key, value in params[0].items()}
        if 'selection' in params:
            polygon_ids = [polygon_id.get_as_int() for polygon_id in params['selection']]
        num_arcs = len(polygon_ids)
        if num_arcs == 0:
            return [('INFO', 'No polygons selected. Select one or more polygons to assign properties.')], []

        # Get the component id map of the selected (if any).
        comp_id = -1
        multi_label = ''
        if 'id_files' in params:
            if params['id_files'] and params['id_files'][0]:
                files_dict = {
                    'POLYGON': (params['id_files'][0].get_as_string(), params['id_files'][1].get_as_string())
                }
                self.load_coverage_component_id_map(files_dict)
                target_type = TargetType.polygon
                try:
                    selected_comp_ids = list(self.comp_to_xms[self.cov_uuid][target_type].keys())
                    comp_id = selected_comp_ids[0] if selected_comp_ids else -1
                    if len(selected_comp_ids) > 1:
                        multi_label = 'Multiple polygons will be assigned the same material.'
                except KeyError:
                    comp_id = -1  # No component ids assigned for any of the selected polygons
        single_polygon = self.data.coverage_data.where(self.data.coverage_data.material_id == comp_id, drop=True)
        material_names = list(self.data.coverage_data.name.values)
        material_ids = list(self.data.coverage_data.material_id.values)
        if single_polygon.user_option.size == 0:
            # Here we are using component id 0 for default values.
            single_polygon = self.data.coverage_data.where(self.data.coverage_data.material_id == 0, drop=True)
        material_index = material_names.index(single_polygon.name[0])
        dialog = AssignPolyMaterialDialog(win_cont, icon, 'Assign Material', multi_label,
                                          material_names, material_index)
        if dialog.exec_():
            new_material_index = dialog.get_selected_material()
            new_material_id = int(material_ids[new_material_index])
            for polygon_id in polygon_ids:
                self.update_component_id(TargetType.polygon, polygon_id, new_material_id)
            self.display_option_list.append(
                XmsDisplayMessage(file=self.disp_opts_file, edit_uuid=self.cov_uuid)
            )
            self.data.commit()

        # Delete the id dumped by xms files.
        shutil.rmtree(os.path.join(os.path.dirname(self.main_file), 'temp'), ignore_errors=True)

        return [], []

    def open_materials(self, query, params, win_cont, icon):
        """Shows the materials dialog.

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
        ids = list(self.data.coverage_data.material_id.values)
        dlg = MaterialDialog('Materials', win_cont, icon, self.data)
        if dlg.exec_():
            new_ids = list(self.data.coverage_data.material_id.values)
            deleted_ids = [int(x) for x in self.update_display_id_files(ids, new_ids)]
            self.unassign_materials(query, deleted_ids)
            # write files
            category_list = self._get_category_list()
            write_display_options_to_json(self.disp_opts_file, category_list)
            self.display_option_list.append(
                XmsDisplayMessage(
                    file=self.disp_opts_file, edit_uuid=self.cov_uuid,
                )
            )
        return [], []

    def _get_category_list(self):
        """Get the category list for the materials."""
        category_list = CategoryDisplayOptionList()
        category_list.target_type = TargetType.polygon
        category_list.comp_uuid = self.uuid
        category_list.uuid = str(self.data.info.attrs['display_uuid'])
        texture_list = list(self.data.coverage_data.texture.values)
        red_list = list(self.data.coverage_data.red.values)
        green_list = list(self.data.coverage_data.green.values)
        blue_list = list(self.data.coverage_data.blue.values)
        name_list = list(self.data.coverage_data.name.values)
        id_list = list(self.data.coverage_data.material_id.values)
        for texture, red, green, blue, name, material_id in zip(texture_list, red_list, green_list, blue_list,
                                                                name_list, id_list):
            category = CategoryDisplayOption()
            category.id = int(material_id)
            category.description = name
            category.file = f'display_ids/material_{category.id}.matid'
            options = PolygonOptions()
            options.texture = PolygonTexture(int(texture))
            options.color = QColor(int(red), int(green), int(blue), 255)
            category.options = options
            # Make unassigned material the default category.
            if category.id == 0:  # Should always have 0 as "material id"
                category.is_unassigned_category = True
            category_list.categories.append(category)
        return category_list

    def update_display_id_files(self, old_ids, new_ids):
        """Update the display files.

        Args:
            old_ids (list): list of ids before editing materials
            new_ids (list): list of current material ids

        Returns:
            (list) : deleted ids
        """
        deleted_ids = old_ids
        path = os.path.join(os.path.dirname(self.main_file), 'display_ids')
        for mat_id in new_ids:
            if mat_id >= 0:
                id_file = f'material_{mat_id}.matid'
                filename = os.path.join(path, id_file)
                write_display_option_ids(filename, [mat_id])
            if mat_id in deleted_ids:
                deleted_ids.remove(mat_id)

        for mat_id in deleted_ids:
            id_file = f'material_{mat_id}.matid'
            filename = os.path.join(path, id_file)
            os.remove(filename)
        return deleted_ids

    def unassign_materials(self, query, delete_ids):
        """Get the coverage UUID from XMS and send back the display options list.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            delete_ids (:obj:`list'): List of the deleted material ids.

        Returns:
            Empty message and ActionRequest lists

        """
        files_dict = self.query_for_all_component_ids(query, TargetType.polygon)
        if self.cov_uuid in self.comp_to_xms and TargetType.polygon in self.comp_to_xms[self.cov_uuid]:
            poly_map = self.comp_to_xms[self.cov_uuid][TargetType.polygon]
            for mat in delete_ids:
                if mat in poly_map:
                    for att_id in poly_map[mat]:
                        self.update_component_id(TargetType.polygon, att_id, MaterialData.UNASSIGNED_MAT)
