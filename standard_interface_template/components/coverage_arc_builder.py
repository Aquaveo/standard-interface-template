"""CoverageArcBuilder class."""
# 1. Standard python modules

# 2. Third party modules

# 3. Aquaveo modules
from data_objects.parameters import Arc, Point

# 4. Local modules

__copyright__ = "(C) Copyright Aquaveo 2020"
__license__ = "All rights reserved"


class CoverageArcBuilder:
    """Creates an arc for a coverage."""

    def __init__(self, node_locs, next_point_id=1, next_arc_id=1, existing_pts=None):
        """
        Constructor.

        Args:
            node_locs: The node locations used by the arc builder.
            next_point_id (int): The next point ID.
            next_arc_id (int): The next arc ID.
            existing_pts(:obj:`dict`): Dictionary of existing points to use in the arc builder.
        """
        self._next_pt_id = next_point_id
        self._next_arc_id = next_arc_id
        self._node_locs = node_locs
        self._pt_map = existing_pts if existing_pts else {}
        self.arcs = []

    def _get_point(self, node_id):
        """
        Get an existing point or create a new one if it hasn't been added yet.

        Args:
            node_id (int): Node id from the geometry.

        Returns:
            data_objects.parameters.Point: Coverage point associated with the passed in geometry node.
        """
        if node_id not in self._pt_map:
            pt = Point(
                self._node_locs[node_id][0],
                self._node_locs[node_id][1],
                self._node_locs[node_id][2]
            )
            pt.set_id(self._next_pt_id)
            self._next_pt_id += 1
            self._pt_map[node_id] = pt
        return self._pt_map[node_id]

    def add_arc(self, start_node_id, end_node_id, vert_list):
        """
        Add an arc to the list of coverage arcs we are building up.

        Ensures we don't get duplicate points in our coverage.

        Args:
            start_node_id (int): Geometry node id of the arc's start node.
            end_node_id (int): Geometry node id of the arc's end node.
            vert_list (list): List of geometry node ids of the arc's vertices.

        Returns:
            int: The XMS feature arc id that was assigned to the new arc.
        """
        arc = Arc()
        att_id = self._next_arc_id
        self._next_arc_id += 1
        arc.set_id(att_id)
        arc.set_start_node(self._get_point(start_node_id))
        arc.set_end_node(self._get_point(end_node_id))
        do_verts = []
        for vert in vert_list:
            do_verts.append(self._get_point(vert))
        arc.set_vertices(do_verts)
        self.arcs.append(arc)
        return att_id
