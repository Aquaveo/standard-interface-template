"""Script to export Standard Interface Template simulation files."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


if __name__ == "__main__":
    import os
    import sys
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QApplication
    from standard_interface_template.gui.feedback.export_simulation_thread import ExportSimulationThread
    from xmsguipy.dialogs.process_feedback_dlg import ProcessFeedbackDlg

    path = os.getcwd()
    worker = ExportSimulationThread(out_dir=path)
    note = ''
    display_text = {
        'title': 'Standard Interface Template Export Simulation',
        'working_prompt': 'Exporting Standard Interface Template simulation files. Please wait...',
        'warning_prompt': 'Warning(s) encountered while exporting simulation. Review log output for more details.',
        'error_prompt': 'Error(s) encountered while exporting simulation. Review log output for more details.',
        'success_prompt': 'Successfully exported simulation',
        'note': note,
        'auto_load': 'Close this dialog automatically when exporting is finished.'
    }
    app = QApplication(sys.argv)
    icon = QIcon()
    feedback_dlg = ProcessFeedbackDlg(icon=icon, display_text=display_text, logger_name='standard_interface_template',
                                      worker=worker, parent=None)
    feedback_dlg.exec()
