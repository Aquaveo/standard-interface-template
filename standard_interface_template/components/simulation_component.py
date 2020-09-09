"""Simulation component class."""
# 1. Standard python modules
import os

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules
from standard_interface_template.components.standard_base_component import StandardBaseComponent
from standard_interface_template.data.simulation_data import SimulationData
from standard_interface_template.gui.dialog import Dialog
# from standard_interface_template.mapping.coverage_mapper_runner import CoverageMapperRunner


__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationComponent(StandardBaseComponent):
    """A hidden Dynamic Model Interface (DMI) component for the Standard Interface Template model simulation."""

    def __init__(self, main_file):
        """Initializes the data class.

        Args:
            main_file: The main file associated with this component.
        """
        super().__init__(main_file)
        self.data = SimulationData(main_file)
        self.class_name = 'SimulationComponent'
        self.module_name = 'standard_interface_template.components.simulation_component'
        #                    [(menu_text, menu_method)...]
        self.tree_commands = [
            ('Model Control...', 'open_model_control'),
            ('Generate Snap Preview', 'create_snap_preview'),
        ]
        if not os.path.isfile(self.main_file):
            self.data.commit()

    def open_model_control(self, query, params, win_cont, icon):
        """Opens the dialog and saves component data state on OK.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            params (:obj:`dict'): Generic map of parameters. Unused in this case.
            win_cont (:obj:`PySide2.QtWidgets.QWidget`): The window container.
            icon (:obj:`PySide2.QtGui.QIcon`): Icon to show in the dialog title

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.

        """
        dialog = Dialog(win_cont, icon, 'Model Control', self.data.info.attrs['user_text'],
                     self.data.info.attrs['user_option'])
        if dialog.exec():
            dlg_data = dialog.get_dialog_data_dict()
            self.data.info.attrs['user_text'] = dlg_data['user_edit']
            self.data.info.attrs['user_option'] = dlg_data['user_display']
            self.data.commit()
        return [], []

    def create_snap_preview(self, query, params, win_cont, icon):
        """Creates mapped components to display Standard Interface Template data on a mesh.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS
            params (:obj:`dict'): Generic map of parameters. Unused in this case.
            win_cont (:obj:`PySide2.QtWidgets.QWidget`): The window container.
            icon (:obj:`PySide2.QtGui.QIcon`): Icon to show in the dialog title

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.

        """
        # note = ''
        # worker = CoverageMapperRunner(query)
        # error_str = 'Error(s) encountered applying coverages to simulation. Review log output for more details.'
        # warning_str = 'Warning(s) encountered applying coverages to simulation. Review log output for more details.'
        # display_text = {
        #     'title': 'Standard Interface Snap Preview',
        #     'working_prompt': 'Applying coverages to mesh. Please wait...',
        #     'error_prompt': error_str,
        #     'warning_prompt': warning_str,
        #     'success_prompt': 'Successfully created snap preview',
        #     'note': note,
        #     'auto_load': 'Close this dialog automatically when exporting is finished.'
        # }
        # feedback_dlg = ProcessFeedbackDlg(icon, display_text, 'standard_interface_template', worker, win_cont)
        # feedback_dlg.exec()
        return [], []
