"""Script to launch a model check of the simulation."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules


if __name__ == "__main__":
    from standard_interface_template.gui.feedback.check_thread import CheckThread
    checker = CheckThread()
    checker.run()
