# -*- coding: utf-8 -*-

"""Code to initialize the internal properties of GraphTransliterator.

This includes the initialization code for tokens rules, onmatch rules, and
whitespace. It also includes the generation of the token regex and them
internal graph...
"""
import math
import re
from .types import TransliterationRule, Whitespace, OnMatchRule, DirectedGraph

# ---------- initialize tokens ----------


def _tokens_of(tokens):
    """Converts values of dict of tokens from list to set."""

    return {key: set(value) for key, value in tokens.items()}

# ---------- initialize rules ----------


def _transliteration_rule_of(rule):
    """Converts rule dict into a TransliterationRule."""

    _cost = _cost_of(rule)

    transliteration_rule = TransliterationRule(
        production=rule.get('production'),
        prev_classes=rule.get('prev_classes'),
        prev_tokens=rule.get('prev_tokens'),
        tokens=rule.get('tokens'),
        next_tokens=rule.get('next_tokens'),
        next_classes=rule.get('next_classes'),
        cost=_cost)

    return transliteration_rule


def _num_tokens_of(rule):
    """Calculate the total number of tokens in a rule."""

    total = 0
    total += len(rule.get('prev_classes', []))
    total += len(rule.get('prev_tokens', []))
    total += len(rule.get('tokens', []))
    total += len(rule.get('next_tokens', []))
    total += len(rule.get('next_classes', []))
    return total


def _cost_of(rule):
    """Calculate the cost of a rule based on the number of constraints.

    Rules requiring more tokens to match are made less costly and tried first.
    """
    return math.log(1+1/(1+_num_tokens_of(rule)))


def _onmatch_rule_of(onmatch_rule):
    """ Converts onmatch_rule into OnMatchRule. """

    return OnMatchRule(prev_classes=onmatch_rule['prev_classes'],
                       next_classes=onmatch_rule['next_classes'],
                       production=onmatch_rule['production'])


def _onmatch_rules_lookup(tokens, onmatch_rules):
    """ Creates a dict lookup from current to previous token.

    Returns
    -------
    list of int
        OnMatchRule indexes valid from this combination
    """

    onmatch_lookup = {}
    # for token_key in tokens:
    #     onmatch_lookup[token_key] = {_: [] for _ in tokens}

    for rule_i, rule in enumerate(onmatch_rules):
        for token_key, token_classes in tokens.items():
            if rule.next_classes[0] in token_classes:
                for prev_token_key, prev_token_classes in tokens.items():
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


def _whitespace_of(whitespace):
    """ Converts whitespace into WhiteSpace """
    return Whitespace(default=whitespace['default'],
                      token_class=whitespace['token_class'],
                      consolidate=whitespace['consolidate'])


# ---------- initialize tokenizer ----------


def _tokenizer_from(tokens):
    """ Generates regular expression tokenizer from token list."""

    tokens.sort(key=len, reverse=True)

    regex_str = '('+'|'.join([re.escape(_) for _ in tokens])+')'

    return re.compile(regex_str, re.S)


# ---------- intialize graph ----------
#


def _graph_from(rules):
    """Generates a parsing graph from the given rules.

    The directed graph is a tree, and the rules are its leaves. Each
    intermediate node represents a token. Before trying to match using a
    token, the constraints on the preceding edge must be met. These include
    token and, on the edge before  a rule, previous and next tokens and token
    classes. The tree is built top-down. Costs of edges are adjust to match
    lowest class of leaf nodes, so they are tried first."""

    graph = DirectedGraph()
    graph.add_node({'type': 'Start'})

    for rule_key, rule in enumerate(rules):
        parent_key = 0
        for token in rule.tokens:
            parent_node = graph.node[parent_key]
            token_children = parent_node.get('token_children') or {}
            token_node_key = token_children.get(token)
            if token_node_key is None:
                token_node_key, _ = graph.add_node(
                    {'type': 'token',
                     'token': token}
                )
                graph.add_edge(
                    parent_key, token_node_key,
                    {'token': token}
                )
                token_children[token] = token_node_key
                parent_node['token_children'] = token_children

            curr_edge = graph.edge[parent_key][token_node_key]
            curr_cost = curr_edge.get('cost') or 1  # costs are > 0, < 1
            if curr_cost > rule.cost:
                curr_edge['cost'] = rule.cost

            parent_key = token_node_key

        rule_node_key, _ = graph.add_node(
            {'type': 'rule',
             'rule_key': rule_key,
             'rule': rule,
             'accepting': True}
        )
        parent_node = graph.node[parent_key]
        rule_children = parent_node.get("rule_children") or []
        rule_children.append(rule_node_key)
        parent_node['rule_children'] = sorted(
            rule_children,
            key=lambda x: graph.node[x]['rule'].cost
        )

        edge_to_rule = graph.add_edge(
                           parent_key, rule_node_key,
                           {'cost': rule.cost}
                       )

        has_constraints = (rule.prev_classes or rule.prev_tokens or
                           rule.next_tokens or rule.next_classes)
        if has_constraints:
            constraints = {}
            if rule.prev_classes:
                constraints['prev_classes'] = rule.prev_classes
            if rule.prev_tokens:
                constraints['prev_tokens'] = rule.prev_tokens
            if rule.next_tokens:
                constraints['next_tokens'] = rule.next_tokens
            if rule.next_classes:
                constraints['next_classes'] = rule.next_classes
            edge_to_rule['constraints'] = constraints

    for node_key, node in graph.node.items():
        ordered_children = {}
        rule_children_keys = node.get('rule_children')

        # add rule children to ordered_children dict under None

        if rule_children_keys:
            ordered_children['__rules__'] = sorted(
                rule_children_keys,
                key=lambda x: graph.edge[node_key][x]['cost'],
            )

        token_children = node.get('token_children')

        # add token children to ordered_children dict

        if token_children:
            for token, token_key in token_children.items():
                ordered_children[token] = [token_key]

                # add rule children there as well

                if rule_children_keys:
                    assert type(rule_children_keys), list
                    ordered_children[token] += rule_children_keys

                # sort both by weight

                ordered_children[token].sort(
                    key=lambda _new_token_key:
                        graph.edge[node_key][_new_token_key]['cost']
                )
            # remove noken children
            node.pop('token_children')
        node['ordered_children'] = ordered_children

    return graph
