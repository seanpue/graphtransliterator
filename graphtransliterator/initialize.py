# -*- coding: utf-8 -*-

"""
Functions used to initialize a GraphTransliterator.
"""
from .graphs import DirectedGraph
from .rules import TransliterationRule, WhitespaceRules, OnMatchRule
from collections import defaultdict
import math
import re
import unicodedata


# ---------- initialize tokens ----------


def _tokens_by_class_of(tokens):
    """Generates lookup table of tokens in each class."""

    out = defaultdict(set)
    for token, token_classes in tokens.items():
        for token_class in token_classes:
            out[token_class].add(token)
    return out


# ---------- initialize rules ----------


def _transliteration_rule_of(rule):
    """Converts rule dict into a TransliterationRule."""

    transliteration_rule = TransliterationRule(
        production=rule.get("production"),
        prev_classes=rule.get("prev_classes"),
        prev_tokens=rule.get("prev_tokens"),
        tokens=rule.get("tokens"),
        next_tokens=rule.get("next_tokens"),
        next_classes=rule.get("next_classes"),
        cost=rule.get("cost", _cost_of(rule)),
    )
    return transliteration_rule


def _num_tokens_of(rule):
    """Calculate the total number of tokens in a rule."""
    total = len(rule.get("tokens"))
    for _ in ("prev_classes", "prev_tokens", "next_tokens", "next_classes"):
        val = rule.get(_)
        if val:
            total += len(val)
    return total


def _cost_of(rule):
    """Calculate the cost of a rule based on the number of constraints.

    Rules requiring more tokens to match are made less costly and tried first.
    """

    return math.log2(1 + 1 / (1 + _num_tokens_of(rule)))


# ---------- initialize onmatch rules ----------


def _onmatch_rule_of(onmatch_rule):
    """Converts onmatch_rule into OnMatchRule."""

    return OnMatchRule(
        prev_classes=onmatch_rule["prev_classes"],
        next_classes=onmatch_rule["next_classes"],
        production=onmatch_rule["production"],
    )


def _onmatch_rules_lookup(tokens, onmatch_rules):
    """Creates a dict lookup from current to previous token.

    Returns
    -------
    dict of {str: dict of {str: list of int}}
        Dictionary keyed by current token to previous token containing a list of
        :class:`OnMatchRule` in order that would apply
    """

    onmatch_lookup = {}

    # Interate through onmatch rules
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


def _whitespace_rules_of(whitespace):
    """Converts whitespace into WhiteSpace"""
    return WhitespaceRules(
        default=whitespace["default"],
        token_class=whitespace["token_class"],
        consolidate=whitespace["consolidate"],
    )


# ---------- initialize tokenizer ----------


def _tokenizer_pattern_from(tokens):
    """Generates regular expression tokenizer pattern from token list.

    Sorts by length and then tokens.
    """

    tokens.sort(key=lambda x: (len(x), x), reverse=True)
    regex_str = "(" + "|".join([re.escape(_) for _ in tokens]) + ")"
    return regex_str


# ---------- initialize graph ----------


def _graph_from(rules):
    """Generates a parsing graph from the given rules.

    The directed graph is a tree, and the rules are its leaves. Each intermediate node
    represents a token. Before trying to match using a token, the constraints on the
    preceding edge must be met. These include tokens and, on the edge before a rule,
    previous and next tokens and token classes. The tree is built top-down. Costs of
    edges are adjusted to match the lowest cost of leaf nodes, so they are tried
    first."""

    graph = DirectedGraph()
    graph.add_node({"type": "Start"})

    for rule_key, rule in enumerate(rules):
        parent_key = 0
        for token in rule.tokens:
            parent_node = graph.node[parent_key]
            token_children = parent_node.get("token_children") or {}
            token_node_key = token_children.get(token)
            if token_node_key is None:
                token_node_key, _ = graph.add_node({"type": "token", "token": token})
                graph.add_edge(parent_key, token_node_key, {"token": token})
                token_children[token] = token_node_key
                parent_node["token_children"] = token_children

            curr_edge = graph.edge[parent_key][token_node_key]
            curr_cost = curr_edge.get("cost", 1)
            if curr_cost > rule.cost:
                curr_edge["cost"] = rule.cost

            parent_key = token_node_key

        rule_node_key, _ = graph.add_node(
            {"type": "rule", "rule_key": rule_key, "accepting": True}  # "rule": rule,
        )
        parent_node = graph.node[parent_key]
        rule_children = parent_node.get("rule_children", [])
        rule_children.append(rule_node_key)
        parent_node["rule_children"] = sorted(
            rule_children, key=lambda x: rules[graph.node[x]["rule_key"]].cost
        )

        edge_to_rule = graph.add_edge(parent_key, rule_node_key, {"cost": rule.cost})

        has_constraints = (
            rule.prev_classes
            or rule.prev_tokens
            or rule.next_tokens
            or rule.next_classes
        )
        if has_constraints:
            constraints = {}
            if rule.prev_classes:
                constraints["prev_classes"] = rule.prev_classes
            if rule.prev_tokens:
                constraints["prev_tokens"] = rule.prev_tokens
            if rule.next_tokens:
                constraints["next_tokens"] = rule.next_tokens
            if rule.next_classes:
                constraints["next_classes"] = rule.next_classes
            edge_to_rule["constraints"] = constraints

    for node_key, node in enumerate(graph.node):
        ordered_children = {}
        rule_children_keys = node.get("rule_children")

        # Add rule children to ordered_children dict under '__rules__''
        if rule_children_keys:
            ordered_children["__rules__"] = sorted(
                rule_children_keys, key=lambda x: rules[graph.node[x]["rule_key"]].cost
            )

            node.pop("rule_children")

        token_children = node.get("token_children")

        # Add token children to ordered_children dict by token
        if token_children:
            for token, token_key in token_children.items():
                ordered_children[token] = [token_key]

                # Add rule children there as well
                if rule_children_keys:
                    ordered_children[token] += rule_children_keys

                # Sort both by cost
                ordered_children[token].sort(
                    key=lambda _new_tkn_key: graph.edge[node_key][_new_tkn_key]["cost"]
                )
            # Remove token_children
            node.pop("token_children")
        node["ordered_children"] = ordered_children

    return graph


# ---------- unicode adjustiments during initialization ----------


def _unescape_charnames(input_str):
    r"""
    Convert \\N{Unicode charname}-escaped str to unicode characters.

    This is useful for specifying exact character names, and a default
    escape feature in Python that needs a function to be used for reading
    from files.

    Parameters
    ----------
    input_str : str
        The unescaped string, with \\N{Unicode charname} converted to
        the corresponding Unicode characters.

    Examples
    --------

    .. jupyter-execute::

      GraphTransliterator._unescape_charnames(r"H\N{LATIN SMALL LETTER I}")

    """

    def get_unicode_char(matchobj):
        """Get Unicode character value from escaped character sequences."""
        charname = matchobj.group(0)
        match = re.match(r"\\N{([-A-Z ]+)}", charname)
        char = unicodedata.lookup(match.group(1))  # KeyError if invalid
        return char

    return re.sub(r"\\N{[-A-Z ]+}", get_unicode_char, input_str)
