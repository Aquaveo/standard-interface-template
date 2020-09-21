"""Exports Standard Interface Template boundary conditions."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class BoundaryConditionsWriter:
    """A class for writing out boundary condition data for the Standard Interface Template."""
    def __init__(self, file_name, arc_to_ids, arc_points, bc_component):
        """Constructor.

        Args:
            file_name (str): The name of the file to write.
            arc_to_ids (dict): The arc to component id of the boundary conditions component.
            arc_points (dict): The arc to node ids of the grid.
            bc_component (BoundaryCoverageComponent): The boundary conditions data to export.
        """
        self._file_name = file_name
        self._data = bc_component
        self._arc_to_component_id = arc_to_ids
        self._arc_to_node_ids = arc_points

    def write(self):
        """Write the simulation file."""
        with open(self._file_name, 'w') as file:
            file.write('###This is a boundary conditions file for Standard Interface Template.###\n')
            df = self._data.data.coverage_data.to_dataframe()
            for arc, component_id in self._arc_to_component_id.items():
                df_row = df.loc[df['comp_id'] == component_id]
                if df_row.empty:
                    # Write default values.
                    file.write(f'BC {arc} A "Hello World!"\n')
                else:
                    # Write values.
                    file.write(f'BC {arc} {df_row.user_option[0]} "{df_row.user_text[0]}"\n')
                file.write('Points:')
                if arc in self._arc_to_node_ids:
                    for node in self._arc_to_node_ids[arc]:
                        file.write(f' {node + 1}')
                file.write('\n')
