"""Uses CoverageMapper to map data to a mesh."""
# 1. Standard python modules
import logging
import os

# 2. Third party modules
from PySide2.QtCore import QThread, Signal

# 3. Aquaveo modules
from xms.constraint import read_grid_from_file

# 4. Local modules
from standard_interface_template.components.boundary_coverage_component import BoundaryCoverageComponent
from standard_interface_template.components.materials_coverage_component import MaterialsCoverageComponent
from standard_interface_template.mapping.coverage_mapper import CoverageMapper

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CoverageMapperRunner(QThread):
    """Class for mapping material coverage to a mesh for Standard Interface."""
    processing_finished = Signal()

    def __init__(self, query):
        """Constructor."""
        super().__init__()
        self._query = query
        self._logger = logging.getLogger('standard_interface_template')

    def run(self):
        """Creates the snap preview of coverages onto the mesh."""
        try:
            context = self._query.get_context()
            self._query.select('mesh')
            self._query.select('Geometry')
            result = self._query.get()['none']
            if not result and result[0]:
                self._logger.info('Mesh not found')
                return
            ugrid_file = result[0].get_xmugrid_file()
            ugrid_uuid = result[0].get_uuid()
            ugrid_wkt = result[0].get_projection().get_well_known_text()
            co_grid = read_grid_from_file(ugrid_file)

            self._query.set_context(context)
            self._query.select('materials_coverage')
            self._query.select('Coverage')
            result = self._query.get()['none']
            materials_coverage = None
            materials_component_file = None
            materials_coverage_component = None
            if not result or not result[0]:
                self._logger.info('Materials Coverage not found')
            else:
                materials_coverage = result[0]
                self._query.select('StandardInterfaceTemplate#Materials_Coverage_Component')
                materials_component_file = self._query.get('main_file')['main_file'][0].get_as_string()
                materials_coverage_component = MaterialsCoverageComponent(materials_component_file)
                materials_coverage_component.load_all_xms_feature_ids_comp_ids(self._query)


            self._query.set_context(context)
            self._query.select('boundary_conditions_coverage')
            self._query.select('Coverage')
            result = self._query.get()['none']
            boundary_conditions_coverage = None
            boundary_conditions_component_file = None
            boundary_conditions_coverage_component = None
            if not result and result[0]:
                self._logger.info('Boundary Conditions Coverage not found')
            else:
                boundary_conditions_coverage = result[0]
                self._query.select('StandardInterfaceTemplate#Boundary_Coverage_Component')
                boundary_conditions_component_file = self._query.get('main_file')['main_file'][0].get_as_string()
                boundary_conditions_coverage_component = BoundaryCoverageComponent(boundary_conditions_component_file)
                boundary_conditions_coverage_component.load_all_xms_feature_ids_comp_ids(self._query)

            if not materials_component_file and not boundary_conditions_component_file:
                return
            elif materials_component_file:
                component_folder = os.path.dirname(os.path.dirname(materials_component_file))
            else:
                component_folder = os.path.dirname(os.path.dirname(boundary_conditions_component_file))

            existing_mapped_component_uuids = []

            self._query.set_context(context)
            self._query.select('Parent')
            self._query.select('materials_mapped_component')
            self._query.select('Component')
            uuid = self._query.get('uuid')['uuid']
            if uuid and uuid[0]:
                uuid_string = uuid[0].get_as_string()
                existing_mapped_component_uuids.append(uuid_string)

            self._query.set_context(context)
            self._query.select('Parent')
            self._query.select('boundary_mapped_component')
            self._query.select('Component')
            uuid = self._query.get('uuid')['uuid']
            if uuid and uuid[0]:
                uuid_string = uuid[0].get_as_string()
                existing_mapped_component_uuids.append(uuid_string)

            query_helper = {'co_grid': co_grid, 'grid_uuid': ugrid_uuid, 'grid_wkt': ugrid_wkt,
                            'component_folder': component_folder,
                            'boundary_condition_coverage': boundary_conditions_coverage,
                            'materials_coverage': materials_coverage,
                            'material_component_file': materials_component_file,
                            'materials_component': materials_coverage_component,
                            'bc_component_file': boundary_conditions_component_file,
                            'bc_component': boundary_conditions_coverage_component}
            worker = CoverageMapper(query_helper, generate_snap=True)
            worker.do_map()

            mapped_comps = worker.mapped_comps
            self._logger.warning(f'Length of mapped components:  {len(mapped_comps)}')
            self._query.set_context(context)
            self._query.select('Parent')
            build_vertex = self._query.add_root_vertex_instance('Build')

            add_vertices = [build_vertex]
            # delete any existing mapped components
            for str_uuid in existing_mapped_component_uuids:
                add_vertices.extend(self._query.add([{'#description': 'Delete', '': str_uuid}],
                                                    self._query.get_context().get_root_instance()))

            for mapped_comp in mapped_comps:  # Will be None if we logged an error during the mapping operation.
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

        except:  # noqa
            self._logger.exception('Error generating snap.')
        finally:
            self.processing_finished.emit()
