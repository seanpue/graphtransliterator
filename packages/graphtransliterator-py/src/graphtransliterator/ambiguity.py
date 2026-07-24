# -*- coding: utf-8 -*-

"""
GraphTransliterator ambiguity-checking functions.
"""

import itertools
import logging
from typing import Any, Protocol

from .exceptions import AmbiguousTransliterationRulesException
from .initialize import _cost_of
from .types import TransliterationRule


# A structural Protocol matching the internal requirements of the Transliterator instance
class TransliteratorLike(Protocol):
    _tokens: dict[str, Any]
    _rules: list[TransliterationRule]
    _tokens_by_class: dict[str, set[str]]


def check_for_ambiguity(transliterator: TransliteratorLike) -> bool:
    """
    Check if multiple transliteration rules could match the same tokens.

    This function first groups the transliteration rules by number of
    tokens. It then checks to see if any pair of the same cost would match
    the same sequence of tokens. If so, it finally checks if a less costly
    rule would match those particular sequences. If not, there is
    ambiguity.

    Details of all ambiguity are sent in a :func:`logging.warning`.
    """
    ambiguity = False

    all_tokens: set[str] = set(transliterator._tokens.keys())

    rules = transliterator._rules

    if not rules:
        return True

    max_prev = [_count_of_prev(rule) for rule in rules]
    global_max_prev = max(max_prev)
    max_curr_next = [_count_of_curr_and_next(rule) for rule in rules]
    global_max_curr_next = max(max_curr_next)

    # Generate a matrix of rules, where width is the max of
    # any previous tokens/classes + max of current/next tokens/classes.
    matrix: list[list[set[str]]] = []

    width = global_max_prev + global_max_curr_next

    for i, rule in enumerate(rules):
        row: list[set[str]] = [all_tokens] * (global_max_prev - max_prev[i])
        row += _tokens_possible(rule, transliterator._tokens_by_class)
        row += [all_tokens] * (width - len(row))
        matrix += [row]

    def full_intersection(i: int, j: int) -> list[set[str]] | None:
        """Intersection of matrix[i] and matrix[j], else None."""
        intersections: list[set[str]] = []
        for k in range(width):
            intersection = matrix[i][k].intersection(matrix[j][k])
            if not intersection:
                return None
            intersections += [intersection]
        return intersections

    def covered_by(intersection: list[set[str]], row: list[set[str]]) -> bool:
        """Check if intersection is covered by row."""
        return all(not intersection[k].difference(row[k]) for k in range(len(intersection)))

    # Helper function to get safe cost
    def get_rule_cost(rule: TransliterationRule) -> float | int:
        cost = rule.get("cost")
        if cost is None:
            return _cost_of(rule)
        return cost

    # Sort enumerated rules by cost before grouping so groupby captures all same-cost rules together
    sorted_enumerated_rules = sorted(enumerate(transliterator._rules), key=lambda x: get_rule_cost(x[1]))

    # Iterate through rules based on cost. If there are ambiguities,
    # check if a less costly rule would match the intersection sequence.
    for _group_val, group_iter in itertools.groupby(sorted_enumerated_rules, key=lambda x: get_rule_cost(x[1])):
        group = list(group_iter)
        if len(group) == 1:
            continue
        for i in range(len(group) - 1):
            for j in range(i + 1, len(group)):
                i_index = group[i][0]
                j_index = group[j][0]
                intersection = full_intersection(i_index, j_index)
                if not intersection:
                    continue

                # Check if a less costly rule matches intersection
                def covered_by_less_costly() -> bool:
                    if intersection is None:
                        return False
                    i_cost = get_rule_cost(rules[i_index])
                    for r_i, r_rule in enumerate(rules):
                        if r_i in (i_index, j_index):
                            continue
                        if get_rule_cost(r_rule) > i_cost:
                            continue
                        rule_tokens = matrix[r_i]
                        if covered_by(intersection, rule_tokens):
                            return True
                    return False

                if not covered_by_less_costly():
                    logging.warning(
                        "The pattern {} can be matched by both:\n  {}\n  {}\n".format(
                            intersection,
                            _easyreading_rule(rules[i_index]),
                            _easyreading_rule(rules[j_index]),
                        )
                    )
                    ambiguity = True

    if ambiguity:
        raise AmbiguousTransliterationRulesException
    return True


def _easyreading_rule(rule: TransliterationRule) -> str:
    """Get an easy-reading string of a rule."""

    def _token_str(x: list[str]) -> str:
        return " ".join(x)

    def _class_str(x: list[str]) -> str:
        return " ".join(["<%s>" % _ for _ in x])

    out = ""
    prev_classes = rule.get("prev_classes")
    prev_tokens = rule.get("prev_tokens")
    tokens = rule.get("tokens", [])
    next_tokens = rule.get("next_tokens")
    next_classes = rule.get("next_classes")

    if prev_classes and prev_tokens:
        out = "({} {}) ".format(_class_str(prev_classes), _token_str(prev_tokens))
    elif prev_classes:
        out = "{} ".format(_class_str(prev_classes))
    elif prev_tokens:
        out = "({}) ".format(_token_str(prev_tokens))

    out += _token_str(tokens)

    if next_tokens and next_classes:
        out += " ({} {})".format(_token_str(next_tokens), _class_str(next_classes))
    elif next_tokens:
        out += " ({})".format(_token_str(next_tokens))
    elif next_classes:
        out += " {}".format(_class_str(next_classes))
    return out


def _count_of_prev(rule: TransliterationRule) -> int:
    """Count previous tokens to be present before a match in a rule."""
    return len(rule.get("prev_classes") or []) + len(rule.get("prev_tokens") or [])


def _count_of_curr_and_next(rule: TransliterationRule) -> int:
    """Count tokens to be matched and those to follow them in rule."""
    return len(rule.get("tokens", [])) + len(rule.get("next_tokens") or []) + len(rule.get("next_classes") or [])


def _prev_tokens_possible(rule: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    """`list` of set of possible preceding tokens for a rule."""
    return [tokens_by_class[_] for _ in rule.get("prev_classes") or []] + [
        set([_]) for _ in rule.get("prev_tokens") or []
    ]


def _curr_and_next_tokens_possible(rule: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    """`list` of sets of possible current and following tokens for a rule."""
    return (
        [set([_]) for _ in rule.get("tokens", [])]
        + [set([_]) for _ in rule.get("next_tokens") or []]
        + [tokens_by_class[_] for _ in rule.get("next_classes") or []]
    )


def _tokens_possible(row: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    """`list` of sets of possible tokens matched for a rule."""
    return _prev_tokens_possible(row, tokens_by_class) + _curr_and_next_tokens_possible(row, tokens_by_class)
