# -*- coding: utf-8 -*-

"""
Functions used to initialize a GraphTransliterator.
"""

import math
import re
import unicodedata
from collections import defaultdict
from typing import Any, Union, cast

from .graphs import DirectedGraph
from .types import (
    ConstraintDict,
    OnMatchRule,
    RawOnMatchDict,
    RawRuleDict,
    RawWhitespaceDict,
    Token,
    TokenClass,
    TransliterationRule,
    WhitespaceRule,
)

# ---------- initialize tokens ----------


def _tokens_by_class_of(tokens: dict[Token, Union[list[TokenClass], set[TokenClass]]]) -> dict[TokenClass, set[Token]]:
    """Generates lookup table of tokens in each class."""

    out: dict[TokenClass, set[Token]] = defaultdict(set)
    for token, token_classes in tokens.items():
        for token_class in token_classes:
            out[token_class].add(token)
    return out


# ---------- initialize rules ----------


def _transliteration_rule_of(rule: RawRuleDict | TransliterationRule) -> TransliterationRule:
    """Converts rule dict into a TransliterationRule."""

    cost = rule.get("cost")
    if cost is None:
        cost = _cost_of(rule)

    transliteration_rule: TransliterationRule = {
        "production": rule.get("production", ""),
        "tokens": rule.get("tokens") or [],
        "cost": cost,
    }

    if rule.get("prev_classes"):
        transliteration_rule["prev_classes"] = rule.get("prev_classes")
    if rule.get("prev_tokens"):
        transliteration_rule["prev_tokens"] = rule.get("prev_tokens")
    if rule.get("next_tokens"):
        transliteration_rule["next_tokens"] = rule.get("next_tokens")
    if rule.get("next_classes"):
        transliteration_rule["next_classes"] = rule.get("next_classes")

    return transliteration_rule


def _num_tokens_of(rule: Union[RawRuleDict, TransliterationRule]) -> int:
    """Calculate the total number of tokens in a rule."""
    tokens_field = rule.get("tokens")
    total = len(tokens_field) if tokens_field else 0

    # Check each optional list field directly to avoid loop type-checking conflicts
    for val in (
        rule.get("prev_classes"),
        rule.get("prev_tokens"),
        rule.get("next_tokens"),
        rule.get("next_classes"),
    ):
        if val:
            total += len(val)
    return total


def _cost_of(rule: Union[RawRuleDict, TransliterationRule]) -> float:
    """Calculate the cost of a rule based on the number of constraints.

    Rules requiring more tokens to match are made less costly and tried first.
    """
    return math.log2(1 + 1 / (1 + _num_tokens_of(rule)))


# ---------- initialize onmatch rules ----------


def _onmatch_rule_of(onmatch_rule: RawOnMatchDict) -> OnMatchRule:
    """Converts onmatch_rule into OnMatchRule."""

    return {
        "prev_classes": onmatch_rule["prev_classes"],
        "next_classes": onmatch_rule["next_classes"],
        "production": onmatch_rule["production"],
    }


def _onmatch_rules_lookup(
    tokens: dict[Token, Union[list[TokenClass], set[TokenClass]]],
    onmatch_rules: list[OnMatchRule],
) -> dict[Token, dict[Token, list[int]]]:
    """Creates a dict lookup from current to previous token.

    Returns
    -------
    dict of {str: dict of {str: list of int}}
        Dictionary keyed by current token to previous token containing a list of
        :class:`OnMatchRule` in order that would apply
    """

    onmatch_lookup: dict[Token, dict[Token, list[int]]] = {}

    # Iterate through onmatch rules
    for rule_i, rule in enumerate(onmatch_rules):
        # Iterate through all tokens
        for token_key, token_classes in tokens.items():
            # if the onmatch rule's next is of that class
            if rule["next_classes"][0] in token_classes:
                # iterate through all tokens again
                for prev_token_key, prev_token_classes in tokens.items():
                    # if second token is of class of onmatch rule's last prev
                    # add the rule to curr -> prev
                    if rule["prev_classes"][-1] in prev_token_classes:
                        if token_key not in onmatch_lookup:
                            onmatch_lookup[token_key] = {}
                        curr_token = onmatch_lookup[token_key]
                        if prev_token_key not in curr_token:
                            curr_token[prev_token_key] = []
                        rule_list = curr_token[prev_token_key]
                        rule_list.append(rule_i)
    return onmatch_lookup


# ---------- initialize whitespace ---------


def _whitespace_rules_of(whitespace: RawWhitespaceDict) -> WhitespaceRule:
    """Converts whitespace into WhiteSpace"""
    return {
        "default": whitespace["default"],
        "token_class": whitespace["token_class"],
        "consolidate": whitespace["consolidate"],
    }


# ---------- initialize tokenizer ----------


def _tokenizer_pattern_from(tokens: list[Token]) -> str:
    """Generates regular expression tokenizer pattern from token list.

    Sorts by length and then tokens.
    """

    tokens.sort(key=lambda x: (len(x), x), reverse=True)
    regex_str = "(" + "|".join([re.escape(_) for _ in tokens]) + ")"
    return regex_str


def _graph_from(rules: list[TransliterationRule]) -> DirectedGraph[Any, Any, Any]:
    """Generates a parsing graph from the given rules."""

    graph: DirectedGraph[Any, Any, Any] = DirectedGraph()

    nodes = cast(list[dict[str, Any]], graph.nodes)
    edges = cast(list[dict[str, Any]], graph.edges)

    # Temporary lookup mapping: source_id -> target_id -> edge_data_dict
    edge_map: dict[int, dict[int, dict[str, Any]]] = defaultdict(dict)

    nodes.append({"type": "Start", "id": 0, "token": "", "label": "Start", "data": {}})

    for rule_key, rule in enumerate(rules):
        rule_cost = rule.get("cost")
        if rule_cost is None:
            rule_cost = _cost_of(rule)

        parent_key = 0
        for token in rule["tokens"]:
            parent_node = nodes[parent_key]
            token_children = parent_node.setdefault("token_children", {})
            token_node_key = token_children.get(token)

            if token_node_key is None:
                token_node_key = len(nodes)
                nodes.append(
                    {
                        "id": token_node_key,
                        "type": "Token",
                        "token": token,
                        "label": token,
                        "data": {},
                    }
                )
                edge_map[parent_key][token_node_key] = {"token": token, "cost": rule_cost}
                token_children[token] = token_node_key

            curr_edge = edge_map[parent_key][token_node_key]
            curr_cost = curr_edge.get("cost")
            if curr_cost is None or rule_cost < curr_cost:
                curr_edge["cost"] = rule_cost

            parent_key = token_node_key

        rule_node_key = len(nodes)
        nodes.append(
            {
                "id": rule_node_key,
                "type": "Rule",
                "token": "",
                "label": f"rule_{rule_key}",
                "rule_key": rule_key,
                "accepting": True,
                "data": {},
            }
        )

        parent_node = nodes[parent_key]
        rule_children = parent_node.setdefault("rule_children", [])
        rule_children.append(rule_node_key)

        edge_map[parent_key][rule_node_key] = {"cost": rule_cost}
        edge_to_rule = edge_map[parent_key][rule_node_key]

        prev_classes = rule.get("prev_classes")
        prev_tokens = rule.get("prev_tokens")
        next_tokens = rule.get("next_tokens")
        next_classes = rule.get("next_classes")

        has_constraints = prev_classes or prev_tokens or next_tokens or next_classes
        if has_constraints:
            constraints: ConstraintDict = {}
            if prev_classes:
                constraints["prev_classes"] = prev_classes
            if prev_tokens:
                constraints["prev_tokens"] = prev_tokens
            if next_tokens:
                constraints["next_tokens"] = next_tokens
            if next_classes:
                constraints["next_classes"] = next_classes
            edge_to_rule["constraints"] = constraints

    for node_key, node in enumerate(nodes):
        ordered_children: dict[str, list[int]] = {}
        rule_children_keys = node.get("rule_children")

        def get_edge_cost(target_key: int) -> float:
            rule_idx = nodes[target_key].get("rule_key")
            if rule_idx is not None:
                r = rules[cast(int, rule_idx)]
                cost = r.get("cost")
                if cost is not None:
                    return float(cost)
                return _cost_of(r)

            raw_cost = edge_map[node_key].get(target_key, {}).get("cost", 0.0)
            return float(raw_cost)

        # Sort rules so the lowest cost (most specific) comes FIRST in the list
        if rule_children_keys:
            ordered_children["__rules__"] = sorted(
                rule_children_keys,
                key=get_edge_cost,
            )
            node.pop("rule_children", None)

        token_children = node.get("token_children")

        if token_children:
            for token, token_key in token_children.items():
                ordered_children[token] = [token_key]

                if rule_children_keys:
                    ordered_children[token] += rule_children_keys

                ordered_children[token].sort(key=get_edge_cost)

            node.pop("token_children", None)

        node["ordered_children"] = ordered_children

    for source_id, targets in edge_map.items():
        for target_id, edge_data in targets.items():
            edges.append(
                {
                    "source": source_id,
                    "target": target_id,
                    "data": edge_data,
                }
            )

    return graph


# ---------- unicode adjustments during initialization ----------


def _unescape_charnames(input_str: str) -> str:
    r"""Convert \\N{Unicode charname}-escaped str to unicode characters."""

    def get_unicode_char(matchobj: re.Match[str]) -> str:
        """Get Unicode character value from escaped character sequences."""
        charname = matchobj.group(0)
        match = re.match(r"\\N{([-A-Z ]+)}", charname)
        if not match:
            return charname
        char = unicodedata.lookup(match.group(1))  # KeyError if invalid
        return cast(str, char)

    return re.sub(r"\\N{[-A-Z ]+}", get_unicode_char, input_str)
