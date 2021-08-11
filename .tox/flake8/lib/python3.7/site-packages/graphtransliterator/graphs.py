# -*- coding: utf-8 -*-
from collections import UserDict, UserList
from .exceptions import IncompleteGraphCoverageException
import logging

"""
Graph data structure used in Graph Transliterator.
"""
logger = logging.getLogger("graphtransliterator")


class DirectedGraph:
    """
    A very basic dictionary- and list-based directed graph. Nodes are a list of
    dictionaries of node data. Edges are nested dictionaries keyed from the
    head -> tail -> edge properties. An edge list is maintained. Can be
    exported as a dictionary.

    Attributes
    ----------
    node : `list` of `dict`
        List of node data
    edge : `dict` of {`int`: `dict` of {`int`: `dict`}}
        Mapping from head to tail of edge, holding edge data

    edge_list : `list` of `tuple` of (`int`, `int`)
        List of head and tail of each edge

    Examples
    -------
    .. jupyter-execute::

      from graphtransliterator import DirectedGraph
      DirectedGraph()

    """

    __slots__ = "edge", "node", "edge_list"

    def __init__(self, node=None, edge=None, edge_list=None):
        self.node = node if node else []
        self.edge = edge if edge else {}
        if edge:
            if not edge_list:
                edge_list = [
                    tuple([head_key, tail_key])
                    for head_key, _ in edge.items()
                    for tail_key in _.keys()
                ]
            self.edge_list = sorted(edge_list)  # sorts for string comparison
        else:
            self.edge_list = []

    def add_edge(self, head, tail, edge_data=None):
        """
        Add an edge to a graph and return its attributes as dict.

        Parameters
        ----------
        head: `int`
            Index of head of edge
        tail: `int`
            Index of tail of edge
        edge_data: `dict`, default {}
            Edge data

        Returns
        -------
        dict
            Data of created edge

        Raises
        ------
        ValueError
            Invalid ``head`` or ``tail``, or ``edge_data`` is not a dict.

        Examples
        --------
        .. jupyter-execute::

          g = DirectedGraph()
          g.add_node()

        .. jupyter-execute::

          g.add_node()

        .. jupyter-execute::

          g.add_edge(0,1, {'data_key_1': 'some edge data here'})

        .. jupyter-execute::

          g.edge

        """
        if edge_data is None:
            edge_data = {}
        if type(head) is not int:
            raise ValueError("Edge head is not an integer: %s." % head)
        if type(tail) is not int:
            raise ValueError("Edge tail is not an integer: %s." % tail)
        if head < 0 or head >= len(self.node):
            raise ValueError("Head index of edge not in graph: %s." % head)
        if tail < 0 or tail >= len(self.node):
            raise ValueError("Tail index of edge not in graph: %s." % tail)
        if type(edge_data) is not dict:
            raise ValueError("Edge data is not a dict: %s." % edge_data)

        if head not in self.edge:
            self.edge[head] = {}

        self.edge[head][tail] = edge_data

        self.edge_list.append(tuple([head, tail]))

        return self.edge[head][tail]

    def add_node(self, node_data=None):
        """Create node and return (`int`, `dict`) of node key and object.

        Parameters
        ----------
        node_data: `dict`, default {}
            Data to be stored in created node

        Returns
        -------
        `tuple` of (`int`, `dict`)
            Index of created node and its data

        Raises
        ------
        ValueError
            ``node_data`` is not a ``dict``

        Examples
        --------
        .. jupyter-execute::

          g = DirectedGraph()
          g.add_node()

        .. jupyter-execute::

          g.add_node({'datakey1': 'data value'})

        .. jupyter-execute::

          g.node

        """
        if node_data is None:
            node_data = {}
        if type(node_data) is not dict:
            raise ValueError("node_data must be a dict: %s" % node_data)
        node_key = len(self.node)
        self.node.append(node_data)
        return node_key, self.node[node_key]


class VisitLoggingList(UserList):
    """Visit logging list."""

    def __init__(self, initlist=None):
        super().__init__(initlist)
        self.visited = set()

    def __getitem__(self, i):
        self.visited.add(i)
        return self.data[i]

    def clear_visited(self):
        self.visited.clear()


class VisitLoggingDict(UserDict):
    """Visit logging dict."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited = set()

    def __getitem__(self, i):
        self.visited.add(i)
        return self.data[i]

    def clear_visited(self):
        self.visited.clear()


class VisitLoggingDirectedGraph(DirectedGraph):
    """A DirectedGraph that logs visits to all nodes and edges.

    Used to measure the coverage of tests for bundled transliterators."""

    def _add_visit_logging(self):
        self.node = VisitLoggingList(self.node)
        # Edges are stored  {HEAD: {TAIL: {DATA}}
        # We only care about {TAIL: DATA} for checking coverage.
        # First, convert all {TAIL: {DATA}} to VisitLoggingDict
        # (This avoids settings {HEAD: {...}} to visited
        for head in self.edge.keys():
            self.edge[head] = VisitLoggingDict(self.edge[head])
        # Second, convert {HEAD: {...}} to VisitLoggingDict
        self.edge = VisitLoggingDict(self.edge)

    def __init__(self, graph):
        """Initialize from existing graph."""
        super().__init__(edge=graph.edge, node=graph.node, edge_list=graph.edge_list)
        self._add_visit_logging()

    def clear_visited(self):
        """Clear all visited attributes on nodes and edges."""
        self.node.visited.clear()
        for head in self.edge.keys():
            self.edge[head].clear_visited()
        self.edge.clear_visited()

    def check_coverage(self, raise_exception=True):
        """Checks that all nodes and edges are visited.

        Parameters
        ----------
        raise_exception: `bool`, default
            Raise IncompleteGraphCoverageException (default, `True`)

        Returns
        -------

        Raises
        ------
        IncompleteGraphCoverageException
            Not all nodes/edges of a graph have been visited."""

        errors = False
        # Check node coverage
        missed_nodes = []
        for node_id in range(len(self.node)):
            if node_id not in self.node.visited:
                errors = True
                missed_nodes.append(node_id)
                node_data = self.node.data[node_id]  # access data so not set to visited
                logger.warning(
                    "Node {} [{}] has not been visited.".format(node_id, node_data)
                )
        # Check edge coverage
        missed_edges = []
        for head in self.edge.keys():
            for tail in self.edge.data[head].keys():  # Access data to not mark visited
                if tail not in self.edge.data[head].visited:
                    errors = True
                    missed_edges.append((head, tail))

                    logger.warning(
                        "Edge ({},{}) [{}] has not been visited.".format(
                            head, tail, self.edge.data[head].data[tail]
                        )
                    )

        # Add a comprehensives error message.
        if errors and raise_exception:
            error_msgs = []
            if missed_nodes:
                error_msgs.append("Missed nodes: " + str(missed_nodes))
            if missed_edges:
                error_msgs.append("Missed edges: " + str(missed_edges))
            raise IncompleteGraphCoverageException("; ".join(error_msgs))

        okay = not errors
        return okay
