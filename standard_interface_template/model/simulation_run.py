"""This module allows SMS to run Standard Interface Template and read its solution on completion."""

# 1. Standard python modules
import os
import shlex
import shutil
import sys

# 2. Third party modules
import h5py

# 3. Aquaveo modules
from data_objects.parameters import Dataset, DsetActivityMappingType, DsetDataMappingType
from xmsapi.dmi import ActionRequest, DialogModality, ExecutableCommand
from xmscomponents.bases.run_base import RunBase

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimulationRun(RunBase):
    """Class that handles running Standard Interface Template.

    """

    def __init__(self, dummy_mainfile=''):
        """Initializes the class.

        Args:
            dummy_mainfile (str): Unused. Just to keep constructor consistent with component classes.

        """
        super().__init__()
        self.project_name = None

    def read_solution(self, query, params, win_cont, icon):
        """Reads the Standard Interface Template Solution.

        Args:
            query (:obj:`data_objects.parameters.Query`): a Query object to communicate with GMS.
            params (:obj:`dict`): Generic map of parameters. Contains the structures for various components that
             are required for adding vertices to the Query Context with Add().
            win_cont (QWidget): The parent window
            icon (QIcon): Icon for the dialog

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        self.project_name = params[0]['project_name'].get_as_string()
        file_location = params[0]['filelocation'].get_as_string()
        return self.read_solution_file(query, file_location)

    def read_solution_file(self, query, file_location):
        """Reads the Standard Interface Template Solution.

        Args:
            query (:obj:`data_objects.parameters.Query`): a Query object to communicate with GMS.
            file_location (str): The directory of the solution to load.

        Returns:
            (:obj:`tuple`): tuple containing:
                - messages (:obj:`list` of :obj:`tuple` of :obj:`str`): List of tuples with the first element of the
                  tuple being the message level (DEBUG, ERROR, WARNING, INFO) and the second element being the message
                  text.
                - action_requests (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): List of actions for XMS to perform.
        """
        messages = []
        return messages, []

    def get_executables(self, sim, query, filelocation):
        """Get the executable commands for any Simulation object given.

        This function will find the correct information that you need for your Simulation object. This function
        determines the correct executables needed, and the correct import scripts needed to load solutions. This
        function determines the correct progress plots needed.

        Args:
            sim (:obj:`data_objects.parameters.Simulation`): The Simulation you want to load the solution for.
            query (:obj:`data_objects.parameters.Query`): a Query object to communicate with GMS.
            filelocation (str): The location of input files for the simulation.

        Returns:
            (:obj:`list` of :obj:`xmsapi.dmi.ExecutableCommand`):
                The executable objects to run and the action requests that go with it.

        """
        # Get the project name
        if not self.project_name:
            self._get_proj_name(query)
        simulation_file = f'{self.project_name}.example_simulation'

        load_sol = self.get_solution_load_actions(sim, query, filelocation)[0]

        cmd = ExecutableCommand()
        cmd.set_executable('SimulationInterfaceTemplate')
        cmd.set_model('SimulationInterfaceTemplate')
        cmd.set_executable_order(0)
        cmd.set_display_name('Simulation Interface Template')
        cmd.set_run_weight(100)
        cmd.add_commandline_argument(simulation_file)
        cmd.set_progress_script('simulation_progress.py')
        cmd.add_solution_file(load_sol)
        commands = [cmd]
        return commands

    def get_solution_load_actions(self, sim, query, filelocation):
        """Get the simulation load ActionRequests for any Simulation object given.

        This method is called when we are loading an existing solution from a previous model run. get_executables is
        called when running or rerunning a simulation.

        Args:
            sim (:obj:`data_objects.parameters.Simulation`): The Simulation you want to load the solution for.
            query (:obj:`data_objects.parameters.Query`): a Query object to communicate with SMS.
            filelocation (str): The location of input files for the simulation.

        Returns:
            (:obj:`list` of :obj:`xmsapi.dmi.ActionRequest`): The solution load ActionRequests for the simulation

        """
        if not self.project_name:
            self._get_proj_name(query)

        # Create an ActionRequest to load the solution located in filelocation
        load_sol = ActionRequest()
        load_sol.SetDialogModality(DialogModality.MODAL)
        load_sol.set_class('SimRunner')
        load_sol.set_module('standard_interface_template.model.sim_runner')
        load_sol.set_main_file('foo')  # Just need a dummy main file for the ActionRequest
        load_sol.set_method_action('read_solution')
        load_sol.set_action_parameter_items({'project_name': self.project_name, 'filelocation': filelocation})
        return [load_sol]

    @staticmethod
    def _ensure_build_edge_exists(build_vertex, query, build_vertices):
        """Make sure a build Context edge has been added to the Query Context.

        Build edge needs to be added before the first Query::Add() call

        Args:
            build_vertex: ?
            query (:obj:`data_objects.parameters.Query`): a Query object to communicate with SMS.
            build_vertices (list): List of the Context vertices that will be flagged for building. Will append the
                root build vertex when added.

        """
        if build_vertex is None:
            build_vertex = query.add_root_vertex_instance('Build')
            build_vertices.append(build_vertex)

        return build_vertex

    def _get_proj_name(self, query):
        """Gets the project name and the temporary directory for the running XMS process.

        Args:
            query (Query): A class to communicate with SMS.
        """
        # Set self.project_name
        proj_result = query.get("project_name")
        if proj_result and proj_result["project_name"] and proj_result["project_name"][0]:
            self.project_name = proj_result["project_name"][0].GetAsString()

        # Get temp directory
        start_ctxt = query.get_context()
        query.select('InstallResources')
        temp_dir = query.get('Temporary Directory')['Temporary Directory']
        if not temp_dir or not temp_dir[0]:
            return
        delete_dir = temp_dir[0].get_as_string()
        self.xms_temp_dir = os.path.join(os.path.dirname(delete_dir), 'Components')
        shutil.rmtree(delete_dir, ignore_errors=True)
        query.set_context(start_ctxt)
