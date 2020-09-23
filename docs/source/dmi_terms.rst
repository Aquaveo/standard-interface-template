Dynamic model interface terminology
===================================

XML and scripts
===============

The model interfaces in XMS are made up of an XML file and multiple scripts that are loaded into
XMS on startup.
The XML file tells XMS which scripts to use for different tasks, as well a information about
the model being interfaced with.
The model interface needs to be in a python package, with a registered entry point, that is
installed in the python area for the XMS program.

Query
=====

Since the scripts are running in different processes than XMS, a way to communicate between them
is needed.
This is where the class Query comes in.
Query allows a script to query for information from XMS, as well as send data back to XMS.

Components
==========

A component in a model interface is an object that can be created by XMS. All components derive
from ComponentBase, or its subclass CoverageComponentBase, in the package xmscomponents.
If a component is part of a coverage or a simulation, but not visible in the project explorer of
XMS, then the component is a hidden component.

Component ids
=============

A component id is an integer id that a component can give to XMS to help identify a specific
feature of a coverage or UGrid. The component id is not the same as the attribute id of the
feature and is never shown to the user. Since the feature's attribute id can change when a user
adds, deletes, splits, or renumbers the feature, the attribute id cannot be stored by the
component reliably. Note that the scripts will **not** be notified when a feature is edited.

For example, lets say that there is a component that keeps track of boundary conditions for
a coverage. The end user specifies a boundary condition for an arc with attribute id 1
(the id you can see in XMS). The component gives the coverage a component id of 7 for the arc.
Then the user splits the arc into two arcs, with attribute ids of 1 and 2. Both arcs now have
component id 7. When the user goes to look at the boundary conditions for arc 2, XMS will give
component id 7 to the script.
