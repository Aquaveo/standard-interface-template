Debugging
=========

Problems
========

As XMS will be launching the scripts, it can be tricky to attach a debugger.
Also, the scripts will be terminated after the call is completed.
The only exception is the ui event loop, which will remain running as long as XMS is running, but will be periodically restarted.

Run a test
==========

Having a unit test that covers the code you wish to debug is a great way to find a fix for problems.

debug_runner.txt
================

Sometimes, when an exception is thrown but not caught, a file called debug_runner.txt wil appear in the temp area for XMS.
This file shows the message from uncaught exceptions.
The is also debug_ui_runner.txt, which has errors that were encountered by the ui event loop.
By default, the temp area can be found by typing "%temp%" in windows explorer, and then navigating to the XMS folder for your running XMS process.
If the setting in preferences has been changed, then the temp area is wherever the preference has it set to.

Inside of the temp area, there is also a folder called "Components".
In this folder there will a folder per component.
The folders will be named with a unique string, with component data inside of it.
If a component threw an uncaught exception, there may be a debug_runner.txt in this folder next to the component data.

Occasionally, there will be a file called debug_run_runner.txt that has a similar purpose, but is specific to errors that occurred trying to run the model executable.
debug_run_runner.txt appears next to the XMS project, instead of the temp area.

Use a debug_pause
=================

Often, it is helpful to use a dialog to pause the execution of program long enough to attach a debugger.
The following code can be added into your repository to aid in debugging::

    def debug_pause():
        """Uses a dialog to pause execution long enough to attach a debugger."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setText('Debug pause.')
        msg.exec()

It should be noted that pausing a script too long can sometimes cause the the ui event loop script, that XMS uses to communicate with scripts, may terminate.
This can cause menus to not appear until the ui event script can be restarted.
In some cases, errors in a model's script can cause the ui event to fail to restart.
This will not work if the code was called from a progress feedback dialog.

time.sleep()
============

Another way to pause execution of the script is to add time.sleep() to your code.
This gives time for a debugger to be attached.
This method of debugging does work with progress feedback dialogs.

Print to file
=============

Debug statements can be written to a file if all else fails.
