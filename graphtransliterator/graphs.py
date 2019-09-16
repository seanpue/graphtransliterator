# -*- coding: utf-8 -*-

"""
Graph data structure used in Graph Transliterator.
"""


class DirectedGraph:
    """
    A very basic dictionary- and list-based directed graph. Nodes are a list of
    dictionaries of node data. Edges are nested dictionaries keyed from the
    head -> tail -> edge properties. An edge list is maintained. Can be
    exported as a dictionary.

    Attributes
    ----------
    node : `list` of `dict`
        List of node attributes
    edge : `dict` of {`int`: `dict` of {`int`: `dict`}}
        Mapping from head to tail of edge, holding edge data
    edge_list : `list` of `tuple` of (`int`, `int`)
        List of head and tail of each edge

    Examples
    -------
    >>> from graphtransliterator import DirectedGraph
    >>> DirectedGraph()
    <graphtransliterator.graphs.DirectedGraph object at 0x106d1c908>
    """

    __slots__ = "edge", "node", "edge_list"

    def __init__(self, edge=None, node=None, edge_list=None):
        if edge or node or edge_list:
            self.edge = edge
            self.node = node
            self.edge_list = edge_list
        else:
            self.edge = {}
            self.node = []
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
        >>> g = DirectedGraph()
        >>> g.add_node()
        (0, {})
        >>> g.add_node()
        (1, {})
        >>> g.add_edge(0,1, {'data_key_1': 'some edge data here'})
        {'data_key_1': 'some edge data here'}
        >>> g.edge
        {0: {1: {'data_key_1': 'some edge data here'}}}
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
        >>> g = DirectedGraph()
        >>> g.add_node()
        (0, {})
        >>> g.add_node({'datakey1': 'data value'})
        (1, {'datakey1': 'data value'})
        >>> g.node
        [{}, {'datakey1': 'data value'}]
        """
        if node_data is None:
            node_data = {}
        if type(node_data) is not dict:
            raise ValueError("node_data must be a dict: %s" % node_data)
        node_key = len(self.node)
        self.node.append(node_data)
        return node_key, self.node[node_key]

    def to_dict(self):
        """Convert graph to a dict, e.g. for serialize.

        Returns
        -------
        dict
            Serialization of graph as a dictionary keyed by:

            ``"edge"``
               Edge data
               (`dict` of {`int`: `dict` of {`int`: `dict`}})

            ``"node"``
                Node data
                (`list` of `dict`)

            ``"edge_list"``
                List of edges
                (`list` of `tuple` (`int`, `int`))

        Examples
        --------
        >>> g = DirectedGraph()
        >>> g.add_node()
        (0, {})
        >>> g.add_node({'datakey1': 'data value'})
        (1, {'datakey1': 'data value'})
        >>> g.node
        [{}, {'datakey1': 'data value'}]
        >>> g.add_edge(0, 1)
        {}
        >>> g.add_edge(1, 0)
        {}
        >>> g.to_dict()
        {'edge': {0: {1: {}}, 1: {0: {}}}, 'node': [{}, {'datakey1': 'data
        value'}], 'edge_list': [(0, 1), (1, 0)]}

        """

        return {"edge": self.edge, "node": self.node, "edge_list": self.edge_list}
