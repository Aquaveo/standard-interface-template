"""Map Material coverage locations and attributes to the Standard Interface domain."""
# 1. Standard python modules
import os
import shutil
import uuid

# 2. Third party modules

# 3. Aquaveo modules
from data_objects.parameters import Component
from xms.snap.snap_polygon import SnapPolygon
from xmscomponents.display.display_options_io import read_display_options_from_json, write_display_options_to_json
from xmscomponents.display.display_options_io import write_display_option_polygon_locations
from xmsguipy.data.category_display_option_list import CategoryDisplayOptionList
from xmsguipy.data.target_type import TargetType

# 4. Local modules
from standard_interface_template.components.materials_mapped_component import MaterialsMappedComponent

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class MaterialMapper:
    """Class for mapping material coverage to a mesh for Standard Interface."""
    def __init__(self, coverage_mapper, wkt, generate_snap):
        """Constructor.

        Args:
            coverage_mapper (:obj:`CoverageMapper`): The container for coverages to map.
            wkt (str): The well known text projection.
            generate_snap (bool): Flag for whether to generate the snap component.
        """
        self._generate_snap = generate_snap
        self._logger = coverage_mapper._logger
        self._co_grid = coverage_mapper.co_grid
        self._new_comp_unique_name = 'Materials_Mapped_Component'
        self._material_component_file = coverage_mapper.material_component.main_file
        self._material_coverage = coverage_mapper.material_coverage
        self._material_component = coverage_mapper.material_component
        self._snap_poly = SnapPolygon()
        self._snap_poly.set_grid(grid=self._co_grid, target_cells=False)
        self._snap_poly.add_polygons(polygons=self._material_coverage.GetPolygons())
        self._comp_main_file = ''
        self._poly_to_cells = {}
        self._comp_path = ''
        self._mat_df = self._material_component.data.coverage_data.to_dataframe()
        self._mat_comp_ids = self._mat_df['material_id'].to_list()
        self._mat_names = self._mat_df['name'].to_list()
        self.mapped_comp_uuid = None
        self.mapped_material_display_uuid = None
        self.grid_wkt = wkt

    def do_map(self):
        """Creates the mapped material component."""
        self._get_polygon_cells()

        if self._generate_snap:
            self._create_component_folder_and_copy_display_options()
            self._create_drawing()

            # Create the data_objects component
            do_comp = Component()
            do_comp.set_main_file(self._comp_main_file)
            do_comp.set_name(f'Snapped {self._material_coverage.get_name()} display')
            do_comp.set_unique_name_and_model_name(self._new_comp_unique_name, 'StandardInterfaceTemplate')
            do_comp.set_locked(False)
            do_comp.set_uuid(os.path.basename(os.path.dirname(self._comp_main_file)))

            comp = MaterialsMappedComponent(self._comp_main_file)
            return do_comp, comp

        return None, None  # pragma: no cover

    def _create_drawing(self):
        """Uses cell ids to get cell point coords to draw polygons for materials mapped to cells."""
        ugrid = self._co_grid.ugrid
        for comp_id, cell_ids in self._poly_to_cells.items():
            poly_list = []
            for cid in cell_ids:
                cell_locs = ugrid.get_cell_locations(cid)
                locs_list = [item for sublist in cell_locs for item in sublist]
                if len(locs_list) < 9:
                    continue  # pragma: no cover
                # repeat the first point
                locs_list.append(locs_list[0])
                locs_list.append(locs_list[1])
                locs_list.append(locs_list[2])
                outer_dict = {'outer': locs_list}
                poly_list.append(outer_dict)
            filename = os.path.join(self._comp_path, f'display_ids/material_{comp_id}.matid')
            write_display_option_polygon_locations(filename, poly_list)

    def _get_polygon_cells(self):
        """Uses xmssnap to get the cells for each polygon."""
        self._logger.info('Mapping material coverage to mesh.')
        num_cells = self._co_grid.ugrid.cell_count
        cell_flag = [True] * num_cells
        polys = self._material_coverage.GetPolygons()
        for poly in polys:
            pid = poly.get_id()
            cells = self._snap_poly.get_cells_in_polygon(pid)
            comp_id = self._material_component.get_comp_id(TargetType.polygon, pid)
            if comp_id is None:
                comp_id = 0  # pragma: no cover
            if comp_id not in self._poly_to_cells:
                self._poly_to_cells[comp_id] = []
            self._poly_to_cells[comp_id].extend(cells)
            for cid in cells:
                cell_flag[cid] = False
        # add all unassigned cells to comp_id = 0 (unassigned_material)
        if 0 not in self._poly_to_cells:
            self._poly_to_cells[0] = []  # pragma: no cover
        for i in range(len(cell_flag)):
            if cell_flag[i]:
                self._poly_to_cells[0].append(i)
        if len(self._poly_to_cells[0]) > 0:
            cells = [x + 1 for x in self._poly_to_cells[0]]
            self._logger.info(f'\n\nThe following elements were assigned to the "unassigned" material.\n'
                              f'Element ids: {cells}.\n')
        for i in range(1, len(self._mat_comp_ids)):
            if self._mat_comp_ids[i] not in self._poly_to_cells or not self._poly_to_cells[self._mat_comp_ids[i]]:
                self._logger.info(f'\n\nMaterial: {self._mat_names[i]} was not assigned to any elements.\n')

    def _create_component_folder_and_copy_display_options(self):
        """Creates a folder for the mapped material component and copies display options from the material coverage."""
        if self.mapped_comp_uuid is None:
            comp_uuid = str(uuid.uuid4())  # pragma: no cover
        else:
            comp_uuid = self.mapped_comp_uuid
        self._logger.info('Creating component folder')
        mat_comp_path = os.path.dirname(self._material_component_file)
        self._comp_path = os.path.join(os.path.dirname(mat_comp_path), comp_uuid)

        if os.path.exists(self._comp_path):
            shutil.rmtree(self._comp_path)  # pragma: no cover
        os.mkdir(self._comp_path)
        os.mkdir(os.path.join(self._comp_path, 'display_ids'))

        mat_comp_display_file = os.path.join(mat_comp_path, 'materials_coverage_display_options.json')
        comp_display_file = os.path.join(self._comp_path, 'materials_coverage_display_options.json')
        if os.path.isfile(mat_comp_display_file):
            shutil.copyfile(mat_comp_display_file, comp_display_file)
            categories = CategoryDisplayOptionList()  # Generates a random UUID key for the display list
            json_dict = read_display_options_from_json(comp_display_file)
            if self.mapped_material_display_uuid is None:
                json_dict['uuid'] = str(uuid.uuid4())  # pragma: no cover
            else:
                json_dict['uuid'] = self.mapped_material_display_uuid
            json_dict['comp_uuid'] = comp_uuid
            json_dict['is_ids'] = 0
            # Set projection of free locations to be that of the mesh/current display
            categories.projection = {'wkt': self.grid_wkt}
            categories.from_dict(json_dict)
            write_display_options_to_json(comp_display_file, categories)
            self._comp_main_file = comp_display_file
        else:
            self._logger.info('Could not find materials_coverage_display_options.json file')  # pragma: no cover
