.. Standard Interface Template documentation master file, created by
   sphinx-quickstart on Tue Sep 22 14:12:28 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Standard Interface Template's documentation!
=======================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Installing the interface
========================

Clone the repository. Go to the python area next to your installed SMS/GMS executable and open a command line prompt.
In the prompt, enter in the following::

   python.exe <path-to-the-interface-repository>/setup.py develop

This should install a develop version of the model interface. Any code changes you make in the repository
will immediately affect the interface in XMS. However, sometimes XMS needs to be restarted in order to see
the changes.

Getting Started
===============

**Replace the model name**

Rename the XML file to something more appropriate for your model. In the XML file, replace:
- “standard_interface_template” with your python module sub-folder name.
- “Standard Interface Template” with the model name that end users will see.
- “standard-interface-template” with your python module name.
- "StandardInterfaceTemplate" with the model name (no spaces) that will be used by XMS to identify it.

**Declare files used by your model**

Change the declare_file elements of the XML.
Change the identifier element in the declare_file element.
Change the input_files and output_files area to only include any files that you want XMS to be able to recognize and read.
In the declare_file elements of the XML, reference the scripts that you want to use to read and write your model files.
Make sure that the name in declare_file is used in the use_file element of either an input_file or an output_file element.

**Export a simulation**

Change simulation_writer.py, geometry_writer.py, boundary_conditions_writer.py, and materials_writer.py.
These file can be changed, removed, or added to accommodate your model.
The code in write_simulation.py sets up a progress feedback dialog so the user can see messages during export.

**Import a simulation**

Change simulation_reader.py, geometry_reader.py, boundary_conditions_reader.py, and materials_reader.py.
These file can be changed, removed, or added to accommodate your model.
The code in read_simulation.py and read_geometry.py sets up a progress feedback dialog so the user can see messages during import.

**Import a solution**

Change the code in SimulationRun.read_solution_file to read the solution file or files of your model.

**Run a simulation**

Change SimulationRun.get_executables to return the executable commands to run as part of your model.
For each executable that could be used as part of your model, make sure there is an executable element for it in the XML.

**Access the model control**

The code for opening the model control is in SimulationComponent.open_model_control, which is in simulation_component.py.
In simulation_dialog.py, simulation_dialog.ui, and simulation_dialog_ui.py is the code
for the model control. The *.ui files are used by Qt and are editable in QtDesigner.

Purpose of the interface
========================

This project can be used as a reference when building your own model interface in XMS.
You can use this project as a template when making your interface.

**Parts**

This model interface defines a simulation, a boundary conditions coverage, and a materials coverage
each with a hidden component. There are also definitions for snap preview components that
show where the boundary conditions and materials are mapped to on the simulation geometry.
The simulation can export files, run a check on how well the simulation is set-up,
run an instance of the model executable with progress, and read its solution.
The model interface also defines how a model can be imported into XMS from its model files.

**Code organization**

The code is organized into the following sub-modules:

- :doc:`check`: How to check a simulation for problems before exporting the files and running the simulation.

- :doc:`components`: The objects that communicate with XMS.

- :doc:`data`: How the data for the components is stored to disk and loaded into memory.

- :doc:`file_io`: How the input files for the simulation run are written from XMS and read into XMS.

- :doc:`gui`: Dialogs that the user will see in XMS.

- :doc:`gui.feedback`: Thread definitions for the process feedback dialog, which displays text and progress for actions.

- :doc:`gui.widgets`: Widgets that are part of one or more dialogs defined in this interface.

- :doc:`mapping`: How coverage features, along with attributes, are mapped to the geometry of the simulation.

- :doc:`simulation_runner`: How to run a simulation.

- :doc:`xml_entry_points`: Scripts that will be run for specific simulation actions.
   - Model check: Checks the simulation for potential problems.
   - Import: Read input files for the model into XMS.
   - Save simulation: Saving the input files for a model run.
   - Progress: Tracking the progress of the simulation as it runs.


How dynamic model interfaces work
=================================

:doc:`dmi_terms`

Best practices
==============

:doc:`best_practices`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
