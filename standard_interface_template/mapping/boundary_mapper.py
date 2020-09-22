"""Map Boundary Conditions coverage locations and attributes to the Standard Interface domain."""
# 1. Standard python modules
import os
import shutil
import uuid

# 2. Third party modules

# 3. Aquaveo modules
from data_objects.parameters import Component
from xms.snap.snap_exterior_arc import SnapExteriorArc
from xmscomponents.display.display_options_io import (read_display_options_from_json, write_display_options_to_json)
from xmscomponents.display.display_options_io import write_display_option_line_locations
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList
from xmsguipy.data.line_style import LineStyle
from xmsguipy.data.target_type import TargetType

# 4. Local modules
from standard_interface_template.components.boundary_mapped_component import BoundaryMappedComponent

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class BoundaryMapper:
    """Class for mapping bc coverage to a mesh for Standard Interface."""
    def __init__(self, coverage_mapper, wkt, generate_snap):
        """
        Constructor.

        Args:
            coverage_mapper (:obj:`CoverageMapper`): The container for coverages to map.
            wkt (str): The well known text projection.
            generate_snap (bool): Flag for whether to generate the snap component.
        """
        self._generate_snap = generate_snap
        self._logger = coverage_mapper._logger
        self._co_grid = coverage_mapper.co_grid
        self._bc_component_file = coverage_mapper.bc_component.main_file
        self._coverage_xml_str = 'boundary_conditions_coverage'
        self._coverage_comp_xml_str = 'StandardInterfaceTemplate#Boundary_Coverage_Component'
        self._new_comp_unique_name = 'Boundary_Mapped_Component'
        self._bc_coverage = coverage_mapper.bc_coverage
        self._bc_component = coverage_mapper.bc_component
        self._snap_arc = SnapExteriorArc()
        self._snap_arc.set_grid(grid=self._co_grid, target_cells=False)
        self._comp_main_file = ''
        self._arc_to_grid_points = {}
        self.arc_id_to_grid_ids = {}
        self._arc_id_to_comp_id = {}
        self._comp_path = ''
        self._grid_wkt = wkt
        self.bc_mapped_comp_uuid = None
        self.bc_mapped_comp_display_uuid = None

    def do_map(self):
        """Creates the mapped bc component."""
        self._get_grid_points_from_arcs()
        if self._generate_snap:
            self._create_component_folder_and_copy_display_options()
            self._create_drawing()
            # Create the data_objects component
            do_comp = Component()
            do_comp.set_main_file(self._comp_main_file)
            do_comp.set_name(f'Snapped {self._bc_coverage.GetName()} display')
            do_comp.set_unique_name_and_model_name(self._new_comp_unique_name, 'StandardInterfaceTemplate')
            do_comp.set_locked(False)
            do_comp.set_uuid(os.path.basename(os.path.dirname(self._comp_main_file)))

            comp = BoundaryMappedComponent(self._comp_main_file)
            return do_comp, comp
        return None, None  # pragma: no cover

    def _create_drawing(self):
        """Uses cell ids to get cell point coords to draw polygons for bc mapped to cells."""
        for disp_name, arcs_list in self._arc_to_grid_points.items():
            filename = os.path.join(self._comp_path, f'display_ids/{disp_name}.display_ids')
            write_display_option_line_locations(filename, arcs_list)

    def _get_grid_points_from_arcs(self):
        """Uses xmssnap to get the points from arcs."""
        self._logger.info('Boundary Condition coverage to mesh.')
        arcs = self._bc_coverage.get_arcs()
        bc_data = self._bc_component.data
        df = bc_data.coverage_data.to_dataframe()
        arc_index = 0
        arc_index_to_arc_id = {}
        for arc in arcs:
            arc_index += 1
            arc_id = arc.get_id()
            arc_index_to_arc_id[arc_index] = arc_id
            comp_id = self._bc_component.get_comp_id(TargetType.arc, arc_id)
            if comp_id is None or comp_id < 0:
                comp_id = 0
                display_name = 'A'
            else:
                df2 = df.loc[df['comp_id'] == comp_id]
                if not df2.empty:
                    display_name = df2.user_option.iloc[0]
                else:
                    display_name = 'A'

            snap_output = self._snap_arc.get_snapped_points(arc)
            if 'location' not in snap_output or not snap_output['location']:
                self._logger.warning(f'Unable to snap arc id: {arc_id} to mesh.')
                continue
            self.arc_id_to_grid_ids[arc_index] = snap_output['id']
            self._arc_id_to_comp_id[arc_index] = comp_id
            points = [item for sublist in snap_output['location'] for item in sublist]

            if display_name not in self._arc_to_grid_points:
                self._arc_to_grid_points[display_name] = []
            self._arc_to_grid_points[display_name].append(points)

    def _create_component_folder_and_copy_display_options(self):
        """Creates the folder for the mapped bc component and copies the display options from the bc coverage."""
        if self.bc_mapped_comp_uuid is None:
            comp_uuid = str(uuid.uuid4())  # pragma: no cover
        else:
            comp_uuid = self.bc_mapped_comp_uuid
        self._logger.info('Creating component folder')
        bc_comp_path = os.path.dirname(self._bc_component_file)
        self._comp_path = os.path.join(os.path.dirname(bc_comp_path), comp_uuid)

        if os.path.exists(self._comp_path):
            shutil.rmtree(self._comp_path)  # pragma: no cover
        os.mkdir(self._comp_path)
        os.mkdir(os.path.join(self._comp_path, 'display_ids'))

        bc_comp_display_file = os.path.join(bc_comp_path, 'boundary_coverage_display_options.json')
        comp_display_file = os.path.join(self._comp_path, 'boundary_coverage_display_options.json')
        if os.path.isfile(bc_comp_display_file):
            shutil.copyfile(bc_comp_display_file, comp_display_file)
            categories = CategoryDisplayOptionList()  # Generates a random UUID key for the display list
            json_dict = read_display_options_from_json(comp_display_file)
            if self.bc_mapped_comp_display_uuid is None:
                json_dict['uuid'] = str(uuid.uuid4())  # pragma: no cover
            else:
                json_dict['uuid'] = self.bc_mapped_comp_display_uuid
            json_dict['comp_uuid'] = comp_uuid
            json_dict['is_ids'] = 0
            categories.from_dict(json_dict)
            categories.projection = {'wkt': self._grid_wkt}

            # Set all snapped arcs to be dashed and thick by default. Keep current color.
            for category in categories.categories:
                category.options.style = LineStyle.DASHEDLINE
                category.options.width = 4
                category.label_on = False

            write_display_options_to_json(comp_display_file, categories)
            self._comp_main_file = comp_display_file
        else:
            self._logger.info('Could not find boundary_coverage_display_options.json file')  # pragma: no cover
