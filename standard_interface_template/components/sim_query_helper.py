"""SimQueryHelper class."""
# 1. Standard python modules
import logging
import os

# 2. Third party modules

# 3. Aquaveo modules
from xms.constraint import read_grid_from_file
import xmsapi.dmi as xmd
from xmsguipy.data.target_type import TargetType
from xmsguipy.tree import tree_util

# 4. Local modules
from standard_interface_template.components.boundary_coverage_component import BoundaryCoverageComponent
from standard_interface_template.components.materials_coverage_component import MaterialsCoverageComponent

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class SimQueryHelper:
    """Class used to get data from XMS related to Standard Interface Template."""

    def __init__(self, query):
        """Constructor.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
        """
        self._query = query
        self._start_context = None
        self._sim_uuid = None
        self.sim_comp_file = ''
        self.component_folder = ''
        self.sim_component = None
        if self._query is not None:
            self.sim_comp_file = self._query.get('main_file')['main_file'][0].get_as_string()
            self.component_folder = os.path.dirname(os.path.dirname(self.sim_comp_file))
            from standard_interface_template.components.simulation_component import SimulationComponent
            self.sim_component = SimulationComponent(self.sim_comp_file)
            self._start_context = self._query.get_context()
            self._query.select('Parent')
            self.sim_uuid = self._query.get('uuid')['uuid'][0].get_as_string()
            self._query.set_context(self._start_context)
        self._logger = logging.getLogger('standard_interface_template')
        self.mapped_comps = []  # (list(tuple)): (data objects component, display_options_action, component name)
        self.grid_name = ''
        self.grid_units = ''
        self.grid_uuid = ''
        self.grid_wkt = ''
        self.co_grid = None
        self.existing_mapped_component_uuids = []
        self.boundary_conditions_coverage = None
        self.materials_coverage = None
        self.boundary_conditions_component = None
        self.material_component = None

    def get_simulation_data(self, warn_if_no_mesh):
        """Gets the coverages associated with a simulation.

        Args:
            warn_if_no_mesh (bool): If True, log warning if no mesh linked to the simulation.
        """
        self.get_geometry(warn_if_no_mesh)
        self.get_boundary_conditions_coverage()
        self.get_materials_coverage()
        self._get_coverage_comp_ids()
        self._query.set_context(self._start_context)

    def get_solution_data(self):
        """Get solution datasets for a simulation.

        Returns:
            (:obj:`list`): List of the solution data_object Dataset dumps for this simulation
        """
        dset_dumps = []
        pe_tree = tree_util.get_project_explorer_tree(self._query)
        # Get the simulation tree item.
        sim_item = tree_util.find_tree_node_by_uuid(pe_tree, self.sim_uuid)
        if not sim_item:
            self._logger.error('Unable to find Standard Interface Template solution datasets.')
            return dset_dumps
        sim_name = sim_item.name
        sim_folder = f'{sim_name} (StandardInterfaceTemplate)'
        # Get the mesh root.
        mesh_root = tree_util.item_from_path(pe_tree, 'Project/Mesh Data')
        if not mesh_root:
            self._logger.error('Unable to find Standard Interface Template solution datasets.')
            return dset_dumps
        # Get the simulation solution folder
        solution_folder = tree_util.first_descendant_with_name(mesh_root, sim_folder)
        if not solution_folder:
            self._logger.error('Unable to find Standard Interface Template solution datasets.')
            return dset_dumps
        # Get dumps of all the children datasets
        solution_dsets = tree_util.descendants_of_type(solution_folder, xmd.DatasetItem)
        root_vtx = self._start_context.get_root_instance()
        select_ctx = self._query.get_context()
        select_ctx.clear_place_marks()
        select_ctx.set_place_mark(root_vtx)
        self._query.set_context(select_ctx)
        self._query.select('SelectUuid')
        try:
            for dset in solution_dsets:
                dset_dumps.append(self._query.get(dset.uuid)[dset.uuid][0])
        except Exception:
            self._logger.exception('Error getting solution dataset.')
        self._query.set_context(self._start_context)
        return dset_dumps

    def _get_coverage(self, coverage_parameter, component_parameter):
        """
        Gets the coverage from the query based on the coverage and component parameters.

        Args:
            coverage_parameter (str): Name of the coverage.
            component_parameter (str): Name of the component.

        Returns:
            (data_objects.Coverage, str): XMS coverage object and filename.
        """
        self._logger.info(f'Getting coverage information for {coverage_parameter}')
        self._query.set_context(self._start_context)
        self._query.select(coverage_parameter)
        self._query.select('Coverage')
        result = self._query.get()['none']
        if not result or not result[0]:
            pass
        else:
            coverage = result[0]
            component_file = ''
            if component_parameter:
                self._query.select(f'StandardInterfaceTemplate#{component_parameter}')
                component_file = self._query.get('main_file')['main_file'][0].get_as_string()
                self._query.select('ComponentCoverageIds')
            return coverage, component_file
        return None, None

    def get_boundary_conditions_coverage(self):
        """Gets the boundary conditions coverage and filename."""
        self.boundary_conditions_coverage, filename = self._get_coverage('boundary_conditions_coverage',
                                                                         'Boundary_Coverage_Component')
        if self.boundary_conditions_coverage:
            self.boundary_conditions_component = BoundaryCoverageComponent(filename)
            self._get_all_point_and_arc_ids_comp_ids(self.boundary_conditions_component)

    def get_materials_coverage(self):
        """Gets the materials coverage and filename."""
        self.materials_coverage, filename = self._get_coverage('materials_coverage', 'Materials_Coverage_Component')
        if self.materials_coverage:
            self.material_component = MaterialsCoverageComponent(filename)
            self._get_all_feature_ids_comp_ids(self.material_component, TargetType.polygon)

    def get_geometry(self, warn_if_no_mesh):
        """Gets the mesh associated with a simulation.

        Args:
            warn_if_no_mesh (bool): If True, log warning if no mesh linked to the simulation.

        Returns:
            bool:  True if a mesh was found, False if not.
        """
        self._logger.info('Getting mesh from simulation.')
        self._query.set_context(self._start_context)
        self._query.select('mesh')
        self._query.select('Geometry')
        result = self._query.get()['none']
        if not result or not result[0]:
            if warn_if_no_mesh:
                err_str = 'Simulation must have a link to a mesh to execute this command.'
                self._logger.warning(err_str)
            return False
        self.grid_name = result[0].get_name()
        proj = result[0].get_projection()
        unit_str = proj.get_horizontal_units()
        if unit_str == 'METERS':
            self.grid_units = 'GridUnit "METER"'
        elif unit_str in ['FEET (U.S. SURVEY)', 'FEET (INTERNATIONAL)']:
            self.grid_units = 'GridUnit "FOOT"'
        else:
            err_str = 'Unable to get horizontal units from mesh'
            self._logger.error(err_str)
            self._logger.error(f'unit_str: {unit_str}')
            raise RuntimeError(err_str)
        grid_file = result[0].get_xmugrid_file()
        self.grid_uuid = result[0].get_uuid()
        self.grid_wkt = result[0].get_projection().get_well_known_text()
        self.co_grid = read_grid_from_file(grid_file)
        self._logger.info('Mesh successfully loaded.')
        return True

    def get_uuids_of_existing_mapped_components(self):
        """Gets the uuids of any existing mapped components."""
        str_uuids = list()
        str_uuids.append(self._get_uuid_of_existing_mapped_component('materials_mapped_component'))
        str_uuids.append(self._get_uuid_of_existing_mapped_component('boundary_mapped_component'))
        for str_uuid in str_uuids:
            if str_uuid:
                self.existing_mapped_component_uuids.append(str_uuid)

    def _get_coverage_comp_ids(self):
        """Load the component ids for the coverage."""
        if self.boundary_conditions_coverage:
            self._get_all_feature_ids_comp_ids(self.boundary_conditions_component, TargetType.arc)
        if self.materials_coverage:
            self._get_all_feature_ids_comp_ids(self.material_component, TargetType.polygon)

    @staticmethod
    def get_feature_file_dict(query, component, target_type):
        """Returns the file dict for the feature type (point, arc, or polygon).

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
            component: The component.
            target_type (TargetType): The feature type (arc, polygon etc).

        Returns:
            See description.
        """
        key = f'{component.uuid}#{component.cov_uuid}#{int(target_type)}'
        id_res = query.get(key)[key]
        file_dict = {}
        if id_res and id_res[0][0].items():
            file_dict = {
                key.get_as_string(): (value[0].get_as_string(), value[1].get_as_string())
                for key, value in id_res[0][0].items()
            }
        return file_dict

    def _get_all_feature_ids_comp_ids(self, component, target_type):
        """Gets all the xms arc ids and component ids.

        Args:
            component (:obj:`StandardBaseComponent`): E.g. BoundaryCoverageComponent, MaterialsCoverageComponent.
            target_type (TargetType): The feature type (arc, polygon etc).
        """
        self._logger.info('Getting feature ids and component ids for coverage.')
        self.load_component_feature_ids(self._query, component, target_type)

    def _get_all_point_and_arc_ids_comp_ids(self, component):
        """Gets all the xms point and arc ids and component ids.

        Args:
            component (derived from Component): The Component.
        """
        self._logger.info('Getting arc ids and component ids for bc coverage.')
        self.load_component_point_and_arc_ids(self._query, component)

    @staticmethod
    def load_component_feature_ids(query, component, target_type):
        """Loads the component feature (arc, polygon etc.) ids.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
            component (:obj:`StandardBaseComponent`): E.g. BoundaryCoverageComponent, MaterialsCoverageComponent.
            target_type (TargetType): The feature type (arc, polygon etc).
        """
        file_dict = SimQueryHelper.get_feature_file_dict(query, component, target_type)
        component.load_coverage_component_id_map(file_dict)
        SimQueryHelper._remove_id_files(file_dict)

    @staticmethod
    def load_component_point_and_arc_ids(query, obs_comp):
        """Loads the component feature ids.

        Args:
            query (:obj:`xmsapi.dmi.Query`): Object for communicating with XMS.
            obs_comp (ObstructionComponent): The ObstructionComponent.
        """
        file_dict_points = SimQueryHelper.get_feature_file_dict(query, obs_comp, TargetType.point)
        file_dict_arcs = SimQueryHelper.get_feature_file_dict(query, obs_comp, TargetType.arc)
        file_dict = {**file_dict_points, **file_dict_arcs}
        obs_comp.load_coverage_component_id_map(file_dict)
        SimQueryHelper._remove_id_files(file_dict)

    def _query_select_component_coverage_ids(self, coverage_xml_str, coverage_comp_xml_str):
        """Calls select('ComponentCoverageIds') on the query.

        Args:
            coverage_xml_str (str): The take name?
            coverage_comp_xml_str (str): 'StandardInterfaceTemplate#<unique_name>'
        """
        self._query.set_context(self._start_context)
        self._query.select(coverage_xml_str)
        self._query.select('Coverage')
        self._query.select(coverage_comp_xml_str)
        self._query.select('ComponentCoverageIds')

    def _get_uuid_of_existing_mapped_component(self, comp_name):
        """Gets the uuids of any mapped components that are part of this simulation.

        Args:
            comp_name (str): component parameter name from XML.

        Returns:
            None or (str): uuid string of component or None.
        """
        self._query.set_context(self._start_context)
        self._query.select('Parent')
        self._query.select(comp_name)
        self._query.select('Component')
        uuid_result = self._query.get('uuid')['uuid']
        if uuid_result and uuid_result[0]:
            str_uuid = uuid_result[0].get_as_string()
            if self.sim_uuid != str_uuid:
                return str_uuid
        return None

    def add_mapped_components_to_xms(self):
        """Add mapped components to the XMS project."""
        # Add the mapped component to the Context and send back to XMS.
        self._logger.info('Adding mapped display items.')
        if len(self.mapped_comps) < 1:
            return
        self._query.set_context(self._start_context)
        self._query.select('Parent')
        build_vertex = self._query.add_root_vertex_instance('Build')  # Add a build out edge from the simulation
        add_vertices = [build_vertex]
        # delete any existing mapped components
        for str_uuid in self.existing_mapped_component_uuids:
            add_vertices.extend(self._query.add([{'#description': 'Delete', '': str_uuid}],
                                                self._query.get_context().get_root_instance()))

        for mapped_comp in self.mapped_comps:  # Will be None if we logged an error during the mapping operation.
            arg_list = [{'#description': mapped_comp[2]}]
            add_vertices.extend(self._query.add(arg_list, build_vertex))
            arg_list = [{
                '#description': 'Component',
                '': mapped_comp[0],
                'actions': mapped_comp[1]
            }]
            add_vertices.extend(self._query.add(arg_list))

        # Set the place marks of the vertices to build
        ctxt = self._query.get_context()
        ctxt.clear_place_marks()
        for place_mark in add_vertices:
            ctxt.set_place_mark(place_mark)
        self._query.set_context(ctxt)

    def remove_existing_mapped_components(self):
        """Remove any existing mapped components."""
        self._logger.info('Removing existing mapped components.')
        self._query.set_context(self._start_context)
        self._query.select('Parent')
        build_vertex = self._query.add_root_vertex_instance('Build')  # Add a build out edge from the simulation
        add_vertices = [build_vertex]
        # delete any existing mapped components
        for str_uuid in self.existing_mapped_component_uuids:
            add_vertices.extend(self._query.add([{'#description': 'Delete', '': str_uuid}],
                                                self._query.get_context().get_root_instance()))

        # Set the place marks of the vertices to build
        ctxt = self._query.get_context()
        ctxt.clear_place_marks()
        for place_mark in add_vertices:
            ctxt.set_place_mark(place_mark)
        self._query.set_context(ctxt)

    @staticmethod
    def _remove_id_files(file_dict):
        """Removes id files from xms that are referenced in the passed in dictionary.

        Args:
            file_dict (dict): dict with key as string and values as tuple of file names.
        """
        for _, val in file_dict.items():
            for f in val:
                if f:
                    os.remove(f)
