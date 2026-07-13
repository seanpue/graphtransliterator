# -*- coding: utf-8 -*-

"""
Functions used to initialize a GraphTransliterator.
"""

from .graphs import DirectedGraph
from .rules import TransliterationRule, WhitespaceRules, OnMatchRule
from .types import (
    Token,
    TokenClass,
    RawRuleDict,
    RawOnMatchDict,
    RawWhitespaceDict,
    ConstraintDict,
)
from collections import defaultdict
import math
import re
import unicodedata
from typing import Any, Union, cast

# ---------- initialize tokens ----------


def _tokens_by_class_of(tokens: dict[Token, Union[list[TokenClass], set[TokenClass]]]) -> dict[TokenClass, set[Token]]:
    """Generates lookup table of tokens in each class."""

    out: dict[TokenClass, set[Token]] = defaultdict(set)
    for token, token_classes in tokens.items():
        for token_class in token_classes:
            out[token_class].add(token)
    return out


# ---------- initialize rules ----------


def _transliteration_rule_of(rule: RawRuleDict) -> TransliterationRule:
    """Converts rule dict into a TransliterationRule."""

    transliteration_rule = TransliterationRule(
        production=rule.get("production", ""),
        prev_classes=rule.get("prev_classes"),
        prev_tokens=rule.get("prev_tokens"),
        tokens=rule.get("tokens", []),
        next_tokens=rule.get("next_tokens"),
        next_classes=rule.get("next_classes"),
        cost=rule.get("cost", _cost_of(rule)),
    )
    return transliteration_rule


def _num_tokens_of(rule: RawRuleDict) -> int:
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


def _cost_of(rule: RawRuleDict) -> float:
    """Calculate the cost of a rule based on the number of constraints.

    Rules requiring more tokens to match are made less costly and tried first.
    """

    return math.log2(1 + 1 / (1 + _num_tokens_of(rule)))


# ---------- initialize onmatch rules ----------


def _onmatch_rule_of(onmatch_rule: RawOnMatchDict) -> OnMatchRule:
    """Converts onmatch_rule into OnMatchRule."""

    return OnMatchRule(
        prev_classes=onmatch_rule["prev_classes"],
        next_classes=onmatch_rule["next_classes"],
        production=onmatch_rule["production"],
    )


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
            if rule.next_classes[0] in token_classes:
                # iterate through all tokens again
                for prev_token_key, prev_token_classes in tokens.items():
                    # if second token is of class of onmatch rule's last prev
                    # add the rule to curr -> prev
                    if rule.prev_classes[-1] in prev_token_classes:
                        if token_key not in onmatch_lookup:
                            onmatch_lookup[token_key] = {}
                        curr_token = onmatch_lookup[token_key]
                        if prev_token_key not in curr_token:
                            curr_token[prev_token_key] = []
                        rule_list = curr_token[prev_token_key]
                        rule_list.append(rule_i)
    return onmatch_lookup


# ---------- initialize whitespace ---------


def _whitespace_rules_of(whitespace: RawWhitespaceDict) -> WhitespaceRules:
    """Converts whitespace into WhiteSpace"""
    return WhitespaceRules(
        default=whitespace["default"],
        token_class=whitespace["token_class"],
        consolidate=whitespace["consolidate"],
    )


# ---------- initialize tokenizer ----------


def _tokenizer_pattern_from(tokens: list[Token]) -> str:
    """Generates regular expression tokenizer pattern from token list.

    Sorts by length and then tokens.
    """

    tokens.sort(key=lambda x: (len(x), x), reverse=True)
    regex_str = "(" + "|".join([re.escape(_) for _ in tokens]) + ")"
    return regex_str


# ---------- initialize graph ----------


def _graph_from(rules: list[TransliterationRule]) -> DirectedGraph:
    """Generates a parsing graph from the given rules."""

    graph = DirectedGraph(node=[], edge={})

    # Use standard dict operations for internal assembly modifications safely
    nodes = cast(list[dict[str, Any]], graph.node)
    edges = cast(dict[int, dict[int, dict[str, Any]]], graph.edge)

    nodes.append({"type": "Start"})

    for rule_key, rule in enumerate(rules):
        parent_key = 0
        for token in rule.tokens:
            parent_node = nodes[parent_key]
            token_children = parent_node.setdefault("token_children", {})
            token_node_key = token_children.get(token)

            if token_node_key is None:
                token_node_key = len(nodes)
                nodes.append({"type": "token", "token": token})
                edges.setdefault(parent_key, {})[token_node_key] = {"token": token}
                token_children[token] = token_node_key

            curr_edge = edges[parent_key][token_node_key]
            curr_cost = curr_edge.get("cost", 1.0)
            if curr_cost > rule.cost:
                curr_edge["cost"] = rule.cost

            parent_key = token_node_key

        rule_node_key = len(nodes)
        nodes.append({"type": "rule", "rule_key": rule_key, "accepting": True})

        parent_node = nodes[parent_key]
        rule_children = parent_node.setdefault("rule_children", [])
        rule_children.append(rule_node_key)
        rule_children.sort(key=lambda x: rules[cast(int, nodes[x]["rule_key"])].cost)

        edges.setdefault(parent_key, {})[rule_node_key] = {"cost": rule.cost}
        edge_to_rule = edges[parent_key][rule_node_key]

        has_constraints = rule.prev_classes or rule.prev_tokens or rule.next_tokens or rule.next_classes
        if has_constraints:
            constraints: ConstraintDict = {}
            if rule.prev_classes:
                constraints["prev_classes"] = rule.prev_classes
            if rule.prev_tokens:
                constraints["prev_tokens"] = rule.prev_tokens
            if rule.next_tokens:
                constraints["next_tokens"] = rule.next_tokens
            if rule.next_classes:
                constraints["next_classes"] = rule.next_classes
            edge_to_rule["constraints"] = constraints

    for node_key, node in enumerate(nodes):
        ordered_children: dict[str, list[int]] = {}
        rule_children_keys = node.get("rule_children")

        # Add rule children to ordered_children dict under '__rules__'
        if rule_children_keys:
            ordered_children["__rules__"] = sorted(
                rule_children_keys,
                key=lambda x: rules[cast(int, nodes[x]["rule_key"])].cost,
            )
            node.pop("rule_children", None)

        token_children = node.get("token_children")

        # Add token children to ordered_children dict by token
        if token_children:
            for token, token_key in token_children.items():
                ordered_children[token] = [token_key]

                # Add rule children there as well
                if rule_children_keys:
                    ordered_children[token] += rule_children_keys

                # Sort both by cost
                ordered_children[token].sort(key=lambda _new_tkn_key: edges[node_key][_new_tkn_key]["cost"])
            # Remove token_children
            node.pop("token_children", None)
        node["ordered_children"] = ordered_children

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
