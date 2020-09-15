"""Script to launch reading of a simulation file."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


if __name__ == "__main__":
    import os
    import sys
    from PySide2.QtGui import (QIcon)
    from PySide2.QtWidgets import (QApplication)
    from standard_interface_template.components.import_simulation_runner import ImportSimulationRunner
    from xmsguipy.dialogs.process_feedback_dlg import ProcessFeedbackDlg

    worker = ImportSimulationRunner()
    note = ''
    display_text = {
        'title': 'Standard Interface Template Import Simulation',
        'working_prompt': 'Importing Standard Interface Template simulation files. Please wait...',
        'warning_prompt': 'Warning(s) encountered while importing simulation. Review log output for more details.',
        'error_prompt': 'Error(s) encountered while importing simulation. Review log output for more details.',
        'success_prompt': 'Successfully imported simulation',
        'note': note,
        'auto_load': 'Close this dialog automatically when importing is finished.'
    }
    app = QApplication(sys.argv)
    icon = QIcon()
    feedback_dlg = ProcessFeedbackDlg(icon=icon, display_text=display_text, logger_name='standard_interface_template',
                                      worker=worker, parent=None)
    feedback_dlg.exec()
