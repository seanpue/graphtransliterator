# -*- coding: utf-8 -*-

"""
Graph classes for GraphTransliterator.
"""

from collections import UserList
import logging
from typing import Any, TypeVar, Union, cast
from .types import NodeData, EdgeData

logger = logging.getLogger("graphtransliterator")

_T = TypeVar("_T")


class DirectedGraph:
    """A directed graph representation containing nodes and edges."""

    def __init__(
        self,
        node: list[NodeData] | None = None,
        edge: dict[int, dict[int, EdgeData]] | None = None,
        edge_list: list[tuple[int, int]] | None = None,
    ) -> None:
        self.node = node if node is not None else []
        self.edge = edge if edge is not None else {}

    def add_edge(self, source: int, target: int, edge_data: EdgeData | None = None) -> None:
        """Add a directed edge with associated metadata between source and target."""
        if not isinstance(source, int) or not isinstance(target, int):
            raise ValueError("Source and target node indices must be integers.")

        if source < 0 or source >= len(self.node) or target < 0 or target >= len(self.node):
            raise ValueError(f"Source node {source} or target node {target} not found in graph.")

        if edge_data is not None and not isinstance(edge_data, dict):
            raise ValueError("Edge data must be a dictionary or None.")

        if source not in self.edge:
            self.edge[source] = {}
        data = edge_data if edge_data is not None else cast(EdgeData, {})
        self.edge[source][target] = data

    def add_node(self, node_data: NodeData | None = None) -> int:
        """Append a node to the graph and return its index."""
        if node_data is not None and not isinstance(node_data, dict):
            raise ValueError("Node data must be a dictionary or None.")

        data = node_data if node_data is not None else cast(NodeData, {})
        self.node.append(data)
        return len(self.node) - 1

    @property
    def edge_list(self) -> list[tuple[int, int]]:
        """Return a list of all edges as (source, target) pairs."""
        return [(int(source), int(target)) for source, targets in self.edge.items() for target in targets]

    @property
    def edges(self) -> list[tuple[int, int]]:
        """Return a list of all edges as (source, target) pairs."""
        return [(int(source), int(target)) for source, targets in self.edge.items() for target in targets]


class OnMatchRuleProxy:
    """A transparent proxy wrapper to log when an OnMatchRule is successfully matched."""

    def __init__(self, obj: Any, idx: int, visited_set: set[int]) -> None:
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_idx", idx)
        object.__setattr__(self, "_visited_set", visited_set)

    def __getattr__(self, name: str) -> Any:
        if name == "production":
            object.__getattribute__(self, "_visited_set").add(object.__getattribute__(self, "_idx"))
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __getitem__(self, item: Any) -> Any:
        val = object.__getattribute__(self, "_obj")[item]
        if (
            hasattr(object.__getattribute__(self, "_obj"), "production")
            and val == object.__getattribute__(self, "_obj").production
        ):
            object.__getattribute__(self, "_visited_set").add(object.__getattribute__(self, "_idx"))
        return val

    def __len__(self) -> int:
        return len(object.__getattribute__(self, "_obj"))

    def __repr__(self) -> str:
        return repr(object.__getattribute__(self, "_obj"))

    def __str__(self) -> str:
        return str(object.__getattribute__(self, "_obj"))


class VisitLoggingList(UserList[_T]):
    """A UserList wrapper that tracks indices of visited elements."""

    def __init__(self, initlist: Union[list[_T], "VisitLoggingList[_T]", None] = None) -> None:
        self.visited: set[int]  # Explicitly declare type before conditional assignments
        if isinstance(initlist, VisitLoggingList):
            super().__init__(initlist.data)
            self.visited = set(initlist.visited)
        else:
            super().__init__(initlist)
            self.visited = set()

        # Wrap each rule inside a proxy to log the visit on successful match
        self.data = [cast(_T, OnMatchRuleProxy(item, i, self.visited)) for i, item in enumerate(self.data)]

    def clear_visited(self) -> None:
        """Reset the visited log tracking."""
        self.visited.clear()


class VisitLoggingDict(dict[Any, Any]):
    """A dictionary wrapper that tracks visited keys across nested lookups."""

    def __init__(
        self,
        data: dict[Any, Any],
        visited_edges: set[tuple[int, int]],
        parent_key: int | None = None,
    ) -> None:
        super().__init__(data)
        self._visited_edges = visited_edges
        self._parent_key = parent_key

    def __getitem__(self, key: Any) -> Any:
        val = super().__getitem__(key)
        if self._parent_key is None:
            if isinstance(val, dict) and not isinstance(val, VisitLoggingDict):
                wrapped = VisitLoggingDict(val, self._visited_edges, parent_key=int(key))
                self[key] = wrapped
                return wrapped
        else:
            self._visited_edges.add((self._parent_key, int(key)))
        return val


class VisitLoggingDirectedGraph(DirectedGraph):
    """A DirectedGraph subclass that monitors runtime traversal over nodes and edges."""

    def __init__(self, graph: DirectedGraph) -> None:
        super().__init__(graph.node, graph.edge)
        self.visited_nodes: set[int] = set()
        self.visited_edges: set[tuple[int, int]] = set()
        self.edge = VisitLoggingDict(graph.edge, self.visited_edges)

    def clear_visited(self) -> None:
        """Reset tracked graph metadata."""
        self.visited_nodes.clear()
        self.visited_edges.clear()

    def check_coverage(self, raise_exception: bool = True) -> bool:
        """Check if all edges present in the underlying graph configuration were traversed."""
        missing_edges: list[tuple[int, int]] = []
        for u, v in self.edges:
            if (u, v) not in self.visited_edges:
                logger.warning(f"Edge ({u} -> {v}) was never visited during runtime.")
                missing_edges.append((u, v))

        if missing_edges and raise_exception:
            from .exceptions import IncompleteGraphCoverageException

            edge_str = ", ".join(f"{u}->{v}" for u, v in missing_edges)
            raise IncompleteGraphCoverageException(f"Incomplete graph edge coverage: {edge_str}")

        return len(missing_edges) == 0
