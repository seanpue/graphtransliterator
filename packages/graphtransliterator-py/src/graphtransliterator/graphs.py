"""
Graph classes for GraphTransliterator.
"""

import logging
from collections import UserList
from typing import Any, Generic, TypeVar, Union, cast

from .types import E, Edge, LoadedGraphDict, N, Node, NodeId, NodeLabel, T

logger = logging.getLogger("graphtransliterator")

_T = TypeVar("_T")


class DirectedGraph(Generic[T, N, E]):
    """A directed graph representation storing nodes and edges in a flat structure."""

    def __init__(
        self,
        nodes: list[Node[T, N]] | None = None,
        edges: list[Edge[E]] | None = None,
    ) -> None:
        self.nodes: list[Node[T, N]] = nodes if nodes is not None else []
        self.edges: list[Edge[E]] = edges if edges is not None else []

    def add_node(
        self,
        data: N | None = None,
        token: Any = None,
        type: Any = None,
        label: NodeLabel | None = None,
        **kwargs: Any,
    ) -> NodeId:
        """Append a node to the graph and return its generated integer NodeId."""
        next_id: NodeId = len(self.nodes)
        if data is not None and not isinstance(data, dict):
            raise ValueError("Node data must be a dictionary or None.")

        new_node: Node[T, N] = cast(
            Node[T, N],
            {"id": next_id, "data": data, "token": token, "type": type, "label": label, **kwargs},
        )
        self.nodes.append(new_node)
        return next_id

    def get_node(self, node_id: NodeId) -> Node[T, N] | None:
        """Return node by numeric NodeId if present."""
        if 0 <= node_id < len(self.nodes):
            return self.nodes[node_id]
        return None

    def add_edge(
        self,
        source: NodeId,
        target: NodeId,
        data: E | None = None,
    ) -> None:
        """Add a directed edge connecting a source NodeId to a target NodeId."""
        if not isinstance(source, int) or not isinstance(target, int):
            raise ValueError("Source and target node indices must be integers.")

        if source < 0 or source >= len(self.nodes) or target < 0 or target >= len(self.nodes):
            raise ValueError(f"Source node {source} or target node {target} not found in graph.")

        if data is not None and not isinstance(data, dict):
            raise ValueError("Edge data must be a dictionary or None.")

        # Ensure a fresh, non-shared dict is created when data is None
        actual_data: E = cast(E, dict(data) if data is not None else {})

        new_edge: Edge[E] = {
            "source": source,
            "target": target,
            "data": actual_data,
        }
        self.edges.append(new_edge)

    def get_edge(self, source: NodeId, target: NodeId) -> dict[str, Any] | None:
        """Return the edge payload or full edge structure connecting source and target.

        Args:
            source: The source node identifier.
            target: The target node identifier.

        Returns:
            The edge's ``data`` dictionary if it is a dict, or the full edge structure
            dict if ``data`` is not a dictionary. Returns ``None`` if no matching edge exists.

        Note:
            For backward compatibility, if an edge's ``data`` property contains a non-dict
            value (e.g., a primitive string), the method returns the full edge dictionary
            (including ``source``, ``target``, and ``data`` keys) rather than just the payload.
        """
        for edge in self.edges:
            if edge["source"] == source and edge["target"] == target:
                data = edge.get("data")
                if isinstance(data, dict):
                    return cast(dict[str, Any], data)
                return cast(dict[str, Any], edge)
        return None

    @property
    def edge_list(self) -> list[tuple[NodeId, NodeId]]:
        """Return a list of all edge connection coordinates as (source, target) tuples."""
        return [(edge["source"], edge["target"]) for edge in self.edges]

    def to_dict(self) -> LoadedGraphDict[T, N, E]:
        """Export graph layout as canonical flat dictionary matching TypeScript."""
        return cast(
            LoadedGraphDict[T, N, E],
            {
                "nodes": self.nodes,
                "edges": self.edges,
            },
        )


class OnMatchRuleProxy:
    """A transparent proxy wrapper to log when an OnMatchRule is matched."""

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
            and val == object.__getattribute__(self, "_obj")["production"]
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
    """A UserList wrapper tracking visited element indices."""

    def visit(self, index: int) -> None:
        """Mark an index as visited."""
        self.visited.add(index)

    def __init__(self, initlist: Union[list[_T], "VisitLoggingList[_T]", None] = None) -> None:
        self.visited: set[int]
        if isinstance(initlist, VisitLoggingList):
            super().__init__(initlist.data)
            self.visited = set(initlist.visited)
        else:
            super().__init__(initlist)
            self.visited = set()

        self.data = [cast(_T, OnMatchRuleProxy(item, i, self.visited)) for i, item in enumerate(self.data)]

    def clear_visited(self) -> None:
        """Reset visited log entries."""
        self.visited.clear()


class VisitLoggingDirectedGraph(DirectedGraph[T, N, E]):
    """Subclass monitoring runtime traversal over nodes and edges."""

    def __init__(self, graph: DirectedGraph[T, N, E]) -> None:
        super().__init__(graph.nodes, graph.edges)
        self.visited_nodes: set[NodeId] = set()
        self.visited_edges: set[tuple[NodeId, NodeId]] = set()

    def visit_node(self, node_id: NodeId) -> None:
        """Log traversal of a node."""
        self.visited_nodes.add(node_id)

    def visit_edge(self, source: NodeId, target: NodeId) -> None:
        """Log traversal of an edge connection."""
        self.visited_edges.add((source, target))

    def clear_visited(self) -> None:
        """Reset tracked graph metadata."""
        self.visited_nodes.clear()
        self.visited_edges.clear()

    def check_coverage(self, raise_exception: bool = True) -> bool:
        """Validate if all edges in graph configuration were traversed."""
        missing_edges: list[tuple[NodeId, NodeId]] = []
        for source, target in self.edge_list:
            if (source, target) not in self.visited_edges:
                logger.warning(f"Edge ({source} -> {target}) was never visited during runtime.")
                missing_edges.append((source, target))

        if missing_edges and raise_exception:
            from .exceptions import IncompleteGraphCoverageException

            edge_str = ", ".join(f"{u}->{v}" for u, v in missing_edges)
            raise IncompleteGraphCoverageException(f"Incomplete graph edge coverage: {edge_str}")

        return len(missing_edges) == 0
