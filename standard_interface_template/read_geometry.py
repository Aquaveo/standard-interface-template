"""Script to launch reading of a geometry file."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules

if __name__ == "__main__":
    import os
    import sys
    from PySide2.QtGui import (QIcon)
    from PySide2.QtWidgets import (QApplication)
    from standard_interface_template.components.import_geometry_runner import ImportGeometryRunner
    from xmsguipy.dialogs.process_feedback_dlg import ProcessFeedbackDlg

    worker = ImportGeometryRunner()
    note = ''
    display_text = {
        'title': 'Standard Interface Template Import Geometry',
        'working_prompt': 'Importing Standard Interface Template geometry files. Please wait...',
        'warning_prompt': 'Warning(s) encountered while importing geometry. Review log output for more details.',
        'error_prompt': 'Error(s) encountered while importing geometry. Review log output for more details.',
        'success_prompt': 'Successfully imported geometry',
        'note': note,
        'auto_load': 'Close this dialog automatically when importing is finished.'
    }
    app = QApplication(sys.argv)
    icon = QIcon()
    feedback_dlg = ProcessFeedbackDlg(icon=icon, display_text=display_text, logger_name='standard_interface_template',
                                      worker=worker, parent=None)
    feedback_dlg.exec()
