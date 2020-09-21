"""Script to launch model check."""
if __name__ == "__main__":
    from standard_interface_template.gui.feedback.check_thread import CheckThread
    checker = CheckThread()
    checker.run_check()
