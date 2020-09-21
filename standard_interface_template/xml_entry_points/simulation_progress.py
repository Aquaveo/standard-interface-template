"""Script to launch Standard Interface Template progress."""

if __name__ == "__main__":
    from standard_interface_template.simulation_runner.progress_tracker import ProgressTracker
    tracker = ProgressTracker()
    tracker.start_tracking()
