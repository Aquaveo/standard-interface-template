# """Map locations and attributes of all linked coverages to the Standard Interface domain."""
# # 1. Standard python modules
# import logging
#
# # 2. Third party modules
#
# # 3. Aquaveo modules
#
# # 4. Local modules
# from standard_interface_template.data.material_data import MaterialData
# from standard_interface_template.mapping.bc_mapper import BcMapper
# from standard_interface_template.mapping.material_mapper import MaterialMapper
#
# __copyright__ = "(C) Copyright Aquaveo 2020"
# __license__ = "All rights reserved"
#
#
# class CoverageMapper:
#     """Class for mapping coverages to a mesh for Standard Interface."""
#     def __init__(self, query_helper, generate_snap):
#         """Constructor."""
#         super().__init__()
#         self._logger = logging.getLogger('standard_interface_template')
#         self._generate_snap = generate_snap
#
#         self.grid_units = query_helper.grid_units
#         self.grid_name = query_helper.grid_name
#         self.co_grid = query_helper.co_grid
#         self.grid_uuid = query_helper.grid_uuid
#         self.grid_wkt = query_helper.grid_wkt
#         self.component_folder = query_helper.component_folder
#         self.ceiling_file = None
#
#         mat_cov = query_helper.coverages.get('material_coverage', [None, None])
#         self.material_coverage = mat_cov[0]
#         self.material_component_file = mat_cov[1]
#         self.material_component = query_helper.material_component
#         self.material_comp_id_to_grid_cell_ids = None
#         self.material_names = None
#         self.material_mannings = None
#         self.mapped_material_uuid = None
#         self.mapped_material_display_uuid = None
#
#         bc_cov = query_helper.coverages.get('bc_coverage', [None, None])
#         self.bc_coverage = bc_cov[0]
#         self.bc_component_file = bc_cov[1]
#         self.bc_component = query_helper.bc_component
#         self.bc_arc_id_to_grid_ids = None
#         self.bc_arc_id_to_comp_id = None
#         self.bc_arc_id_to_bc_param = None
#         self.bc_arc_id_to_bc_id = None
#         self.bc_id_to_structures = None
#         self.bc_mapped_comp_uuid = None
#         self.bc_mapped_comp_display_uuid = None
#
#         self.mapped_comps = []
#
#     def do_map(self):
#         """Creates the snap preview of coverages onto the mesh."""
#         try:
#             self._map_materials()
#             self._map_sed_materials()
#             self._map_bc()
#             self._map_monitor()
#             self._map_obstructions()
#         except:  # pragma: no cover  # noqa
#             self._logger.exception('Error generating snap.')  # pragma: no cover
#
#     def _map_materials(self):
#         """Maps the materials from the material coverage to the mesh."""
#         if self.material_coverage is None or not self.material_component_file:
#             return
#         self._logger.info('Mapping materials coverage to mesh.')
#         mapper = MaterialMapper(self, wkt=self.grid_wkt, sediment=False, generate_snap=self._generate_snap)
#         mapper.mapped_comp_uuid = self.mapped_material_uuid
#         mapper.mapped_material_display_uuid = self.mapped_material_display_uuid
#         self.material_comp_id_to_grid_cell_ids = mapper._poly_to_cells
#         mat_data = MaterialData(self.material_component_file)
#         self.material_names = mat_data.materials.to_dataframe()['Name'].tolist()
#         do_comp, comp = mapper.do_map()
#         self.material_mannings = mapper._mannings_n
#         if do_comp is not None:
#             self.mapped_comps.append((do_comp, [comp.get_display_options_action()],
#                                      'mapped_material_component'))
#         self._logger.info('Finished mapping materials coverage to mesh.')
#
#     def _map_bc(self):
#         """Maps the boundary conditions from the boundary conditions coverage to the mesh."""
#         if self.bc_coverage is None or not self.bc_component_file:
#             return
#         self._logger.info('Mapping bc coverage to mesh.')
#         mapper = BcMapper(self, wkt=self.grid_wkt, generate_snap=self._generate_snap)
#         mapper.ceiling_file = self.ceiling_file
#         mapper.bc_mapped_comp_uuid = self.bc_mapped_comp_uuid
#         mapper.bc_mapped_comp_display_uuid = self.bc_mapped_comp_display_uuid
#         self.bc_arc_id_to_grid_ids = mapper.arc_id_to_grid_ids
#         self.bc_arc_id_to_comp_id = mapper._arc_id_to_comp_id
#         self.bc_arc_id_to_bc_param = mapper._arc_id_to_bc_param
#         self.bc_arc_id_to_bc_id = mapper._arc_id_to_bc_id
#         self.bc_id_to_structures = mapper._structures
#         do_comp, comp = mapper.do_map()
#         if do_comp is not None:
#             self.mapped_comps.append((do_comp, [comp.get_display_options_action()],
#                                      'mapped_bc_component'))
#         self._logger.info('Finished mapping bc coverage to mesh.')
