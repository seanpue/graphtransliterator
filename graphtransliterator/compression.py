# -*- coding: utf-8 -*-
"""
Functions used to compress and decompress a GraphTransliterator.
"""
import math


def compress_config(config, compression_level=1):
    """
    Compress configuration to minimize JSON size.

    Compression uses integer lookup for classes, tokens, and graph node types, as well
    as numerous tuples. It contains the graph definition but not easily generatable
    items.


    Parameters
    ----------
    config : `dict`
        Configuration of GraphTransliterator, e.g. from `dump` or `loads`.

    Returns
    -------
    `tuple`
        Compressed configuration consisting of:

            Class names : `tuple` of `str`
                Provides id of classes when compressed to integer index

            Token strings : (`tuple` of `str`)
                Provides id of tokens when compressed to integer index

            Token classes : (`tuple` of `int`) or 0 (`int`) for None

            Production rules : (`tuple` of `tuple`)

                Production: `str`

                Previous class ids : (`tuple` of `int`) or 0 (`int`) for None

                Previous token ids : (`tuple` of `int`) or 0 (`int`) for None

                Token ids : (`tuple` of `int`)

                Next token ids : (`tuple` of `int`) or 0 (`int`) for None

                Next class ids : (`tuple` of `int`) or 0 (`int`) for None

            Cost : Negative integer cost (`int`)

            Graph : `tuple`

                Node types : `tuple` of `str`
                    Provides id of node types when compressed to integer index

                Nodes : `tuple` of `tuple`
                    All node types begin with the following fields:

                        Node type id : `int`
                        Accepting: 0 or 1 (`int`) for False or True

                    `Start` nodes additionally contain:

                        Ordered Children : `dict` of token to node ids {`int`: `int`}
                            The rules key (`__rules__`) is -1

                    `rule` nodes additionally contain:
                        Rule key: `int`

                    `token` nodes additionally contain:

                        Token id: `int`

                        Ordered Children: `dict` of token to node ids {`int`: `int`}

                            The rules key (`__rules__`) is -1

                Edges: `dict` of {`int`: `dict` of {`int`: `tuple`}}

                    Dictionary points from head id to tail id to edge data. The data
                    consists of the following:

                        Constraints: `tuple` or `0` (`int`) for None

                            Previous classes : class ids (`list` of `int`), or 0 (`int`)

                            Previous tokens : token ids (`list` of `int`), or 0 (`int`)

                            Next tokens: token ids (`list` of `int`), or 0 (`int`)

                            Next classes : class ids (`list` of `int`), or 0 (`int`)

                        Cost : Negative integer cost (`int`)

                        Token: Token id (`int`) or -1 for None
    """

    # No compression, human-readable
    if compression_level == 0:
        return config

    def compressed_cost(x):
        return -1 * round((1 / (2**x - 1) - 1))  # convert to -int

    def compress_edge_data(data):
        constraints = data.get("constraints")

        def _class_ids_of(constraint_attr):
            v = constraints.get(constraint_attr)
            if not v:
                return 0
            return [_class_id[_] for _ in v]

        def _token_ids_of(constraint_attr):
            v = constraints.get(constraint_attr)
            if not v:
                return 0
            return [_token_id[_] for _ in v]

        new_constraints = 0

        if constraints:
            new_constraints = [
                _class_ids_of("prev_classes"),
                _token_ids_of("prev_tokens"),
                _token_ids_of("next_tokens"),
                _class_ids_of("next_classes"),
            ]
        new_cost = compressed_cost(data.get("cost"))
        new_token = -1
        _token = data.get("token")
        if _token:
            new_token = _token_id[_token]

        return tuple([new_constraints, new_cost, new_token])

    def compress_node(_node):
        def compressed_ordered_children():
            x = _node.get("ordered_children")
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
            new_node = tuple([_type_id, _accepting, compressed_ordered_children()])
        elif _node["type"] == "rule":
            new_node = tuple([_type_id, _accepting, _node["rule_key"]])
        elif _node["type"] == "token":
            new_node = tuple(
                [
                    _type_id,
                    _accepting,
                    _token_id[_node["token"]],
                    compressed_ordered_children(),
                ]
            )
        return new_node

    token_list = tuple(sorted(config["tokens"].keys()))
    _token_id = {_: i for i, _ in enumerate(token_list)}

    class_list = tuple(sorted(set().union(*config["tokens"].values())))
    _class_id = {_: i for i, _ in enumerate(class_list)}
    tokens = tuple(
        tuple(_class_id[_] for _ in config["tokens"][tkn]) for tkn in token_list
    )
    nodetype_list = tuple(sorted(set([_["type"] for _ in config["graph"]["node"]])))
    _nodetype_id = {_: i for i, _ in enumerate(nodetype_list)}

    rules = tuple(
        (
            r["production"],
            tuple(_class_id[_] for _ in r.get("prev_classes"))
            if r.get("prev_classes")
            else 0,
            tuple(_token_id[_] for _ in r.get("prev_tokens"))
            if r.get("prev_tokens")
            else 0,
            tuple(_token_id[_] for _ in r.get("tokens")),
            tuple(_token_id[_] for _ in r.get("next_tokens"))
            if r.get("next_tokens")
            else 0,
            tuple(_class_id[_] for _ in r.get("next_classes"))
            if r.get("next_classes")
            else 0,
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
        _graph = config.get("graph")
        node = tuple(compress_node(_) for _ in _graph["node"])
        _edge = _graph["edge"]
        edge = {
            int(head_id): {
                int(tail_id): compress_edge_data(edge_data)
                for tail_id, edge_data in tail.items()
            }
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


def _strip_empty(d):
    """Strips entries of dict with no value, but allow zero."""
    return {
        k: v
        for k, v in d.items()
        if v or (type(v) is int and v == 0) or (type(v) is str and v == "")
    }


def decompress_config(compressed_config):
    def decompressed_cost(x):
        """x will be negative."""
        return math.log2(1 + 1 / (1 - x))

    def decompress_node(_node):
        def decompressed_ordered_children(index):
            x = _node[index]
            out = {}
            for k, v in x.items():
                k = int(k)
                if k == -1:
                    out["__rules__"] = v
                else:
                    out[_token_from_id[k]] = v
            return out

        node_type = _nodetype_from_id[_node[0]]
        accepting = True if _node[1] else False
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

    def decompress_edge_data(data):
        [_constraints, _cost, _token] = data

        out = {}

        def _class_from_ids_of(index):
            v = _constraints[index]
            if v == 0:
                return None
            return [_class_from_id[_] for _ in v]

        def _token_from_ids_of(index):
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
    tokens = {
        tkn: [_class_list[_] for _ in _tokens[i]] for i, tkn in enumerate(_token_list)
    }
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
    if not _graph:  # no graph due to compression
        graph = None
    else:
        [_nodetype_list, _nodes, _edges] = _graph
        _nodetype_from_id = {i: _ for i, _ in enumerate(_nodetype_list)}
        node = [decompress_node(_) for _ in _nodes]
        edge = {
            int(head_id): {
                int(tail_id): decompress_edge_data(edge_data)
                for tail_id, edge_data in tail.items()
            }
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
