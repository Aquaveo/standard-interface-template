"""Provide progress feedback when running the Standard Interface Template model in SMS."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules
from xmsapi.dmi import Query

# 4. Local modules


class ProgressTracker:
    """Class that tracks an Standard Interface Template model running in SMS."""
    query = None
    progress_loop = None
    echo_file = None
    echo_pos = 0

    def __init__(self):
        """Does nothing except construct the class."""
        pass

    @staticmethod
    def progress_function():
        """Calculates the progress and sends it to SMS."""
        # Compute the current progress percent.
        progress_percent = 0
        found_percent = False
        if not ProgressTracker.echo_file:
            ProgressTracker.echo_file = ProgressTracker.progress_loop.get_command_line_output_file()

        try:
            with open(ProgressTracker.echo_file, 'r') as f:
                f.seek(ProgressTracker.echo_pos)
                echo_line = f.readline()
                while echo_line:
                    # Check that the line is finished
                    if echo_line.endswith('\n') or echo_line.endswith('\r'):
                        ProgressTracker.echo_pos = f.tell()
                        line_parts = echo_line.split()
                        if len(line_parts) == 2:
                            if line_parts[0] == '%':
                                found_percent = True
                                progress_percent = line_parts[1]
                    echo_line = f.readline()
        except Exception:
            pass  # File might not exist yet

        if found_percent:
            arg_list = [{"": int(progress_percent)}]
            ProgressTracker.query.set(arg_list)
            ProgressTracker.query.send()

    @staticmethod
    def start_tracking():
        """Entry point for the Standard Interface Template progress script."""
        ProgressTracker.query = Query()
        session = ProgressTracker.query.get_xms_agent().get_session()
        ProgressTracker.progress_loop = session.get_progress_loop()
        ProgressTracker.progress_loop.set_progress_function(ProgressTracker.progress_function)
        ProgressTracker.query.set_context(ProgressTracker.progress_loop.get_progress_context())
        ProgressTracker.progress_loop.start_loop()
