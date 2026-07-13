# -*- coding: utf-8 -*-
"""
Functions used to compress and decompress a GraphTransliterator.
"""

import math
from typing import Any, cast, Union

DEFAULT_COMPRESSION_LEVEL = 2
HIGHEST_COMPRESSION_LEVEL = 2

def compress_config(config: dict[str, Any], compression_level: int = 1) -> Any:
    """
    Compress configuration to minimize JSON size.

    Compression uses integer lookup for classes, tokens, and graph node types, as well
    as numerous tuples. It contains the graph definition but not easily generatable
    items.
    """

    # No compression, human-readable
    if compression_level == 0:
        return config

    def compressed_cost(x: float) -> int:
        return -1 * round((1 / (2**x - 1) - 1))  # convert to -int

    def compress_edge_data(data: dict[str, Any]) -> tuple[Any, int, int]:
        constraints: dict[str, Any] | None = data.get("constraints")

        def _class_ids_of(constraint_attr: str) -> Union[list[int], int]:
            if not constraints:
                return 0
            v = constraints.get(constraint_attr)
            if not v:
                return 0
            return [_class_id[_] for _ in v]

        def _token_ids_of(constraint_attr: str) -> Union[list[int], int]:
            if not constraints:
                return 0
            v = constraints.get(constraint_attr)
            if not v:
                return 0
            return [_token_id[_] for _ in v]

        new_constraints: Any = 0

        if constraints:
            new_constraints = [
                _class_ids_of("prev_classes"),
                _token_ids_of("prev_tokens"),
                _token_ids_of("next_tokens"),
                _class_ids_of("next_classes"),
            ]
        new_cost = compressed_cost(data.get("cost", 0.0))
        new_token = -1
        _token = data.get("token")
        if _token:
            new_token = _token_id[_token]

        return tuple([new_constraints, new_cost, new_token])

    def compress_node(_node: dict[str, Any]) -> tuple[Any, ...]:
        def compressed_ordered_children() -> dict[int, Any]:
            x = _node.get("ordered_children", {})
            out = {}
            for k, v in x.items():
                if k == "__rules__":
                    out[-1] = v
                else:
                    out[_token_id[k]] = v
            return out

        _type_id = _nodetype_id[_node["type"]]
        _accepting = 1 if _node.get("accepting") else 0

        if _node["type"] == "Start":
            return tuple([_type_id, _accepting, compressed_ordered_children()])
        elif _node["type"] == "rule":
            return tuple([_type_id, _accepting, _node["rule_key"]])
        elif _node["type"] == "token":
            return tuple(
                [
                    _type_id,
                    _accepting,
                    _token_id[_node["token"]],
                    compressed_ordered_children(),
                ]
            )
        return tuple()

    token_list = tuple(sorted(config["tokens"].keys()))
    _token_id = {_: i for i, _ in enumerate(token_list)}

    class_list = tuple(sorted(set().union(*config["tokens"].values())))
    _class_id = {_: i for i, _ in enumerate(class_list)}
    tokens = tuple(tuple(_class_id[_] for _ in config["tokens"][tkn]) for tkn in token_list)
    nodetype_list = tuple(sorted(set([_["type"] for _ in config["graph"]["node"]])))
    _nodetype_id = {_: i for i, _ in enumerate(nodetype_list)}

    rules = tuple(
        (
            r["production"],
            tuple(_class_id[_] for _ in r.get("prev_classes")) if r.get("prev_classes") else 0,
            tuple(_token_id[_] for _ in r.get("prev_tokens")) if r.get("prev_tokens") else 0,
            tuple(_token_id[_] for _ in r.get("tokens")),
            tuple(_token_id[_] for _ in r.get("next_tokens")) if r.get("next_tokens") else 0,
            tuple(_class_id[_] for _ in r.get("next_classes")) if r.get("next_classes") else 0,
            compressed_cost(r["cost"]),
        )
        for r in config["rules"]
    )
    whitespace = tuple(
        [
            config["whitespace"]["default"],
            config["whitespace"]["token_class"],
            1 if config["whitespace"]["consolidate"] else 0,
        ]
    )
    onmatch_rules = (
        tuple(
            tuple(
                [
                    tuple(_class_id[_] for _ in r["prev_classes"]),
                    tuple(_class_id[_] for _ in r["next_classes"]),
                    r["production"],
                ]
            )
            for r in config["onmatch_rules"]
        )
        if config.get("onmatch_rules")
        else 0
    )
    metadata = config.get("metadata", 0)

    if compression_level == 1:
        # Compress with generated graph; no information loss.
        _graph = config.get("graph", {})
        node = tuple(compress_node(_) for _ in _graph.get("node", []))
        _edge = _graph.get("edge", {})
        edge = {
            int(head_id): {int(tail_id): compress_edge_data(edge_data) for tail_id, edge_data in tail.items()}
            for head_id, tail in _edge.items()
        }

        return tuple(
            [
                class_list,
                token_list,
                tokens,
                rules,
                whitespace,
                onmatch_rules,
                metadata,
                [nodetype_list, node, edge],
            ]
        )
    elif compression_level == 2:
        # Compress without graph; no information loss.
        return tuple(
            [
                class_list,
                token_list,
                tokens,
                rules,
                whitespace,
                onmatch_rules,
                metadata,
                None,
            ]
        )
    return tuple()


def _strip_empty(d: dict[str, Any]) -> dict[str, Any]:
    """Strips entries of dict with no value, but allow zero."""
    return {k: v for k, v in d.items() if v or (type(v) is int and v == 0) or (type(v) is str and v == "")}


def decompress_config(compressed_config: tuple[Any, ...]) -> dict[str, Any]:
    def decompressed_cost(x: float) -> float:
        """x will be negative."""
        return math.log2(1 + 1 / (1 - x))

    def decompress_node(_node: tuple[Any, ...]) -> dict[str, Any]:
        def decompressed_ordered_children(index: int) -> dict[str, Any]:
            x = _node[index]
            out = {}
            for k, v in x.items():
                k_int = int(k)
                if k_int == -1:
                    out["__rules__"] = v
                else:
                    out[_token_from_id[k_int]] = v
            return out

        node_type = _nodetype_from_id[_node[0]]
        accepting = True if _node[1] else False
        new_node: dict[str, Any] = {}
        if node_type == "Start":
            new_node = {
                "type": node_type,
                "accepting": accepting,
                "ordered_children": decompressed_ordered_children(2),
            }
        elif node_type == "rule":
            new_node = {"type": node_type, "accepting": accepting, "rule_key": _node[2]}
        elif node_type == "token":
            new_node = {
                "type": node_type,
                "accepting": accepting,
                "token": _token_from_id[_node[2]],
                "ordered_children": decompressed_ordered_children(3),
            }
        return _strip_empty(new_node)

    def decompress_edge_data(data: tuple[Any, ...]) -> dict[str, Any]:
        [_constraints, _cost, _token] = data

        out: dict[str, Any] = {}

        def _class_from_ids_of(index: int) -> list[str] | None:
            v = _constraints[index]
            if v == 0:
                return None
            return [_class_from_id[_] for _ in v]

        def _token_from_ids_of(index: int) -> list[str] | None:
            v = _constraints[index]
            if v == 0:
                return None
            return [_token_from_id[_] for _ in v]

        if _constraints:
            # filter out unused values
            out["constraints"] = _strip_empty(
                {
                    "prev_classes": _class_from_ids_of(0),
                    "prev_tokens": _token_from_ids_of(1),
                    "next_tokens": _token_from_ids_of(2),
                    "next_classes": _class_from_ids_of(3),
                }
            )

        out["cost"] = decompressed_cost(_cost)

        if _token != -1:  # -1 indicates no token
            out["token"] = _token_from_id[_token]

        return out

    [
        _class_list,
        _token_list,
        _tokens,
        _rules,
        _whitespace,
        _onmatch_rules,
        metadata,
        _graph,
    ] = compressed_config

    _token_list = list(_token_list)
    _token_from_id = {i: _ for i, _ in enumerate(_token_list)}
    _class_list = list(_class_list)
    _class_from_id = {i: _ for i, _ in enumerate(_class_list)}
    tokens = {tkn: [_class_list[_] for _ in _tokens[i]] for i, tkn in enumerate(_token_list)}
    rules = [
        _strip_empty(
            {
                "production": _[0],
                "prev_classes": [_class_list[i] for i in _[1]] if _[1] else [],
                "prev_tokens": [_token_list[i] for i in _[2]] if _[2] else [],
                "tokens": [_token_list[i] for i in _[3]],
                "next_tokens": [_token_list[i] for i in _[4]] if _[4] else [],
                "next_classes": [_class_list[i] for i in _[5]] if _[5] else [],
                "cost": decompressed_cost(_[6]),
            }
        )
        for _ in _rules
    ]
    whitespace = {
        "default": _whitespace[0],
        "token_class": _whitespace[1],
        "consolidate": _whitespace[2],
    }
    onmatch_rules = (
        [
            {
                "prev_classes": [_class_from_id[_] for _ in r[0]],
                "next_classes": [_class_from_id[_] for _ in r[1]],
                "production": r[2],
            }
            for r in _onmatch_rules
        ]
        if _onmatch_rules
        else None
    )
    
    graph: dict[str, Any] | None = None
    if _graph:
        [_nodetype_list, _nodes, _edges] = _graph
        _nodetype_from_id = {i: _ for i, _ in enumerate(_nodetype_list)}
        node = [decompress_node(_) for _ in _nodes]
        edge = {
            int(head_id): {int(tail_id): decompress_edge_data(edge_data) for tail_id, edge_data in tail.items()}
            for head_id, tail in _edges.items()
        }
        graph = {"node": node, "edge": edge}

    return {
        "tokens": tokens,
        "rules": rules,
        "whitespace": whitespace,
        "onmatch_rules": onmatch_rules,
        "graph": graph,
        "metadata": metadata,
    }