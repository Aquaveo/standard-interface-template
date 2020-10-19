"""Script to launch Standard Interface Template progress."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


if __name__ == "__main__":
    from standard_interface_template.simulation_runner.progress_tracker import ProgressTracker
    tracker = ProgressTracker()
    tracker.start_tracking()
