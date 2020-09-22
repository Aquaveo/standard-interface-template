"""Map locations and attributes of all linked coverages to the Standard Interface domain."""
# 1. Standard python modules
import logging

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules
from standard_interface_template.mapping.boundary_mapper import BoundaryMapper
from standard_interface_template.mapping.material_mapper import MaterialMapper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CoverageMapper:
    """Class for mapping coverages to a mesh for Standard Interface."""
    def __init__(self, query_helper, generate_snap):
        """
        Constructor.

        Args:
            query_helper (:obj:`SimQueryHelper`): Values queried to use in the coverage mapper.
            generate_snap (bool): Whether or not snap preview components are generated.
        """
        super().__init__()
        self._logger = logging.getLogger('standard_interface_template')
        self._generate_snap = generate_snap

        self.co_grid = query_helper.co_grid
        self.grid_uuid = query_helper.grid_uuid
        self.grid_wkt = query_helper.grid_wkt
        self.component_folder = query_helper.component_folder

        self.material_coverage = query_helper.materials_coverage
        self.material_component = query_helper.material_component
        self.material_comp_id_to_grid_cell_ids = None
        self.material_names = None
        self.mapped_material_uuid = None
        self.mapped_material_display_uuid = None

        self.bc_coverage = query_helper.boundary_conditions_coverage
        self.bc_component = query_helper.boundary_conditions_component
        self.bc_arc_id_to_grid_ids = None
        self.bc_arc_id_to_comp_id = None
        self.bc_arc_id_to_bc_id = None
        self.bc_mapped_comp_uuid = None
        self.bc_mapped_comp_display_uuid = None

        self.query_helper = query_helper

    def do_map(self):
        """Creates the snap preview of coverages onto the mesh."""
        try:
            self._map_materials()
            self._map_boundary_conditions()
        except:  # pragma: no cover  # noqa
            self._logger.exception('Error generating snap.')  # pragma: no cover

    def _map_materials(self):
        """Maps the materials from the material coverage to the mesh."""
        if self.material_coverage is None:
            return
        self._logger.info('Mapping materials coverage to mesh.')
        mapper = MaterialMapper(self, wkt=self.grid_wkt, generate_snap=self._generate_snap)
        mapper.mapped_comp_uuid = self.mapped_material_uuid
        mapper.mapped_material_display_uuid = self.mapped_material_display_uuid
        self.material_comp_id_to_grid_cell_ids = mapper._poly_to_cells
        mat_data = self.material_component.data
        self.material_names = mat_data.coverage_data.to_dataframe()['name'].tolist()
        do_comp, comp = mapper.do_map()
        if do_comp is not None:
            self.query_helper.mapped_comps.append((do_comp, [comp.get_display_options_action()],
                                                  'materials_mapped_component'))
        self._logger.info('Finished mapping materials coverage to mesh.')

    def _map_boundary_conditions(self):
        """Maps the boundary conditions from the boundary conditions coverage to the mesh."""
        if self.bc_coverage is None:
            return
        self._logger.info('Mapping bc coverage to mesh.')
        mapper = BoundaryMapper(self, wkt=self.grid_wkt, generate_snap=self._generate_snap)
        mapper.bc_mapped_comp_uuid = self.bc_mapped_comp_uuid
        mapper.bc_mapped_comp_display_uuid = self.bc_mapped_comp_display_uuid
        self.bc_arc_id_to_grid_ids = mapper.arc_id_to_grid_ids
        self.bc_arc_id_to_comp_id = mapper._arc_id_to_comp_id
        do_comp, comp = mapper.do_map()
        if do_comp is not None:
            self.query_helper.mapped_comps.append((do_comp, [comp.get_display_options_action()],
                                                  'boundary_mapped_component'))
        self._logger.info('Finished mapping boundary conditions coverage to mesh.')
