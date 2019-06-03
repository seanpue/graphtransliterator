# -*- coding: utf-8 -*-
"""Types used by GraphTransliterator."""


from collections import namedtuple

# ---------- Transliterator rule ----------


class TransliterationRule(namedtuple('TransliterationRule',
                                     ['production',
                                      'prev_classes',
                                      'prev_tokens',
                                      'tokens',
                                      'next_tokens',
                                      'next_classes',
                                      'cost'])):
    """
    Transiteration rule.

    Contains both the production (output) and the specific conditions that
    must be matched.

    Attributes
    ----------
    production: str
        Output from the `TransliterationRule`
    prev_classes: list of str or None
        List of previous token classes to be matched before `tokens` or,
        if they exist, `prev_tokens`
    prev_tokens: list of str or None
        List of tokens to be matched before `tokens`
    tokens: list of str
        list of tokens to match
    next_tokens: list of str or None
        list of tokens to match after `tokens`
    next_classes: list of str or None
        List of tokens to match after `tokens` or, if they exist, `next_tokens`
    cost: int
        Cost of the rule, where less specific rules are more costly.
    """

    # def __len__(self):
    #     """ Total number of tokens in rule, including before and after. """
    #
    #     return sum(
    #         [len(_) for _ in (
    #             self.prev_classes,
    #             self.prev_tokens,
    #             self.tokens,
    #             self.next_tokens,
    #             self.next_classes
    #          ) if _ is not None]
    #     )

    __slots__ = ()


# ---------- Transliterator output ----------


class TransliteratorOutput(namedtuple('TransliteratorOutput', ['matches',
                                                               'output'])):
    """
    Final output of transliteration, including string and rules matched.

    Attributes
    ----------
    matches: list of TransliterationRule
        List of the Transliterator rule matches
    output: str
        Final output of the GraphTransliterator
    """

    __slots__ = ()


# ---------- on match rule ----------


class OnMatchRule(namedtuple('OnMatchRule', ['prev_classes',
                                             'next_classes',
                                             'production'])):
    """
    Rules about adding text between certain combinations of matched rules.

    The `production` of an `OnMatchRule` is added before the `production` of a
    particular `TransliterationRule`, if the classes of the previous and
    following tokens in the output string match `prev_class` and `next_class`.

    Attributes
    ----------
    prev_classes: list of str
        List of previously matched token classes required
    next_classes: list of str
        List of next token classes required
    production: str
        Text to add before a match between prev_classes and next_classes
    """

    __slots__ = ()


# ---------- whitespace ----------


class Whitespace(namedtuple('Whitespace', ['default',
                                           'token_class',
                                           'consolidate'])):
    """
    Whitespace settings of GraphTransliterator.

    Attributes
    ----------
    default: str
        Default whitespace token
    token_class: str
        Whitespace token class, e.g. for punctuation, spaces, etc.
    consolidate: boolean
        Consolidate whitespace tokens and render as a single instance of
        `default`
    """

    __slots__ = ()


# ---------- directed graph ----------


class DirectedGraph:
    """
    A very basic dictionary- and list-based directed graph.

    Nodes are a list of dictionaries of node data. Edges
    are nested dictionaries keyed from the head -> tail -> edge
    properties. A list of edges consisting of a tuple of
    (head, tail) is also maintained.

    The graph can be exported as a dictionary using
    `DirectedGraph.to_dict`.

    Attributes
    ----------
    node : list of dict
        List of node attributes ordered by zero-indexed node id
    edge : dict of {int: dict of {int: dict}}
        Mapping from head to tail of edge, holding edge data
    edge_list : list of tuple of (int, int)
        List of head and tail of each edge

    """

    __slots__ = 'edge', 'node', 'edge_list'

    def __init__(self):
        self.edge = {}
        self.node = []
        self.edge_list = []

    def add_edge(self, head, tail, edge_data={}):
        """Add edge in graph, edge_list, and return its attributes as dict.

        Parameters
        ----------
        head: int
            Index of head of edge
        tail: int
            Index of tail of edge
        edge_data: dict, default {}
            Edge data

        Returns
        -------
        dict
            Data of created edge

        Raises
        ------
        ValueError
            The `head or `tail` of edge is invalid, or `edge_data` not a dict.
        """
        if type(head) is not int:
            raise ValueError("Edge head is not an integer: %s." % head)
        if type(tail) is not int:
            raise ValueError("Edge tail is not an integer: %s." % tail)
        if head < 0 or head >= len(self.node):
            raise ValueError(
                "Head index of edge not in graph: %s." % head)
        if tail < 0 or tail >= len(self.node):
            raise ValueError("Tail index of edge not in graph: %s." % tail)
        if type(edge_data) is not dict:
            raise ValueError("Edge data is not a dict: %s." % edge_data)

        if head not in self.edge:
            self.edge[head] = {}

        self.edge[head][tail] = edge_data

        self.edge_list.append(tuple([head, tail]))

        return self.edge[head][tail]

    def add_node(self, node_data={}):
        """Create node and return (int, dict) of node key and object.
        Parameters
        ----------
        node_data: dict, default {}
            Data to be stored in created node

        Returns
        -------
        tuple of (int, dict)
            Index of created node and its data

        Raises
        ------
        ValueError
            `node_data` is not a dict
        """

        if not type(node_data) == dict:
            raise ValueError("node_data must be a dict: %s" % node_data)

        node_key = len(self.node)
        self.node.append(node_data)  # self.node[node_key] = node_data
        return node_key, self.node[node_key]

    def to_dict(self):
        """Convert graph to a dict, e.g. for serialize.

        Returns
        -------
        dict
            Serialization of graph as a dictionary keyed by:
               "edge": dict of {int: dict of {int: dict}}
               "node": list of dict
               "edge_list": list of tuple (int, int)
        """

        return {
            "edge": self.edge,
            "node": self.node,
            "edge_list": self.edge_list
        }
