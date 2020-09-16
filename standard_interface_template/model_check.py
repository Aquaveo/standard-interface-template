"""Script to launch model check."""
if __name__ == "__main__":
    from standard_interface_template.components.check_runner import CheckRunner
    checker = CheckRunner()
    checker.run_check()
