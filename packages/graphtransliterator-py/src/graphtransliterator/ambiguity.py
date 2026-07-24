"""
GraphTransliterator ambiguity-checking functions.
"""

import itertools
import logging
from collections import defaultdict
from typing import Any, Protocol

from .exceptions import AmbiguousTransliterationRulesException
from .initialize import _cost_of
from .types import TransliterationRule


class TransliteratorLike(Protocol):
    _tokens: dict[str, Any]
    _rules: list[TransliterationRule]
    _tokens_by_class: dict[str, set[str]]


def check_for_ambiguity(transliterator: TransliteratorLike) -> bool:
    """Check if multiple transliteration rules can match the same token sequence.

    This function constructs a fixed-width matrix representing the possible token
    matches for every rule (including required previous and next context tokens).
    It then identifies rule pairs with equal costs that overlap (have a non-empty
    intersection).

    To avoid false positives, any overlapping pair is checked against lower-cost
    rules; if a less costly rule covers the exact intersection sequence, the overlap
    is resolved by priority and ignored.

    If an overlapping pair of the same cost is **not** covered by any less costly
    rule, a warning is logged detailing the overlapping pattern and the two
    conflicting rules in an easy-to-read format.

    Args:
        transliterator: An object conforming to `TransliteratorLike` containing
            the rule definitions, token mappings, and token classes.

    Returns:
        bool: True if no unresolvable rule ambiguities are found.

    Raises:
        AmbiguousTransliterationRulesException: If one or more unresolvable
            ambiguous rule pairs are detected.

    Side Effects:
        Logs a `logging.warning` for each ambiguous pair found, showing the intersecting
        token pattern and formatted representations of the conflicting rules.
    """

    tokens_by_class = transliterator._tokens_by_class
    rules = transliterator._rules

    if not rules:
        return True

    # Group rules by cost to check for overlapping rules with equal cost
    rules_by_cost = defaultdict(list)
    for rule in rules:
        rules_by_cost[_cost_of(rule)].append(rule)

    ambiguous_pairs = []

    # Calculate maximum dimensions for alignment matrix
    max_prev = max((_count_of_prev(r) for r in rules), default=0)
    max_curr_next = max((_count_of_curr_and_next(r) for r in rules), default=0)

    for cost, cost_rules in rules_by_cost.items():
        if len(cost_rules) < 2:
            continue

        for rule1, rule2 in itertools.combinations(cost_rules, 2):
            p1_count = _count_of_prev(rule1)
            p2_count = _count_of_prev(rule2)

            p1_poss = _prev_tokens_possible(rule1, tokens_by_class)
            p2_poss = _prev_tokens_possible(rule2, tokens_by_class)

            cn1_poss = _curr_and_next_tokens_possible(rule1, tokens_by_class)
            cn2_poss = _curr_and_next_tokens_possible(rule2, tokens_by_class)

            # Check overlap across aligned slots
            shift1_p = max_prev - p1_count
            shift2_p = max_prev - p2_count

            overlap = True
            for i in range(max_prev + max_curr_next):
                s1 = None
                if i < max_prev:
                    idx = i - shift1_p
                    if idx >= 0:
                        s1 = p1_poss[idx]
                else:
                    idx = i - max_prev
                    if idx < len(cn1_poss):
                        s1 = cn1_poss[idx]

                s2 = None
                if i < max_prev:
                    idx = i - shift2_p
                    if idx >= 0:
                        s2 = p2_poss[idx]
                else:
                    idx = i - max_prev
                    if idx < len(cn2_poss):
                        s2 = cn2_poss[idx]

                if s1 is not None and s2 is not None:
                    if not (s1 & s2):
                        overlap = False
                        break

            if overlap:
                ambiguous_pairs.append((rule1, rule2))

    if ambiguous_pairs:
        for r1, r2 in ambiguous_pairs:
            logging.warning(
                f"Ambiguous rules detected:\n  Rule 1: {_easyreading_rule(r1)}\n  Rule 2: {_easyreading_rule(r2)}"
            )
        raise AmbiguousTransliterationRulesException("Ambiguous transliteration rules found.")

    return True


def _easyreading_rule(rule: TransliterationRule) -> str:
    def _token_str(x: list[str]) -> str:
        return " ".join(x)

    def _class_str(x: list[str]) -> str:
        return " ".join([f"<{_}>" for _ in x])

    out = ""
    prev_classes = rule.get("prev_classes")
    prev_tokens = rule.get("prev_tokens")
    tokens = rule.get("tokens", [])
    next_tokens = rule.get("next_tokens")
    next_classes = rule.get("next_classes")

    if prev_classes and prev_tokens:
        out = f"({_class_str(prev_classes)} {_token_str(prev_tokens)}) "
    elif prev_classes:
        out = f"{_class_str(prev_classes)} "
    elif prev_tokens:
        out = f"({_token_str(prev_tokens)}) "

    out += _token_str(tokens)

    if next_tokens and next_classes:
        out += f" ({_token_str(next_tokens)} {_class_str(next_classes)})"
    elif next_tokens:
        out += f" ({_token_str(next_tokens)})"
    elif next_classes:
        out += f" {_class_str(next_classes)}"
    return out


def _count_of_prev(rule: TransliterationRule) -> int:
    return len(rule.get("prev_classes") or []) + len(rule.get("prev_tokens") or [])


def _count_of_curr_and_next(rule: TransliterationRule) -> int:
    return len(rule.get("tokens", [])) + len(rule.get("next_tokens") or []) + len(rule.get("next_classes") or [])


def _prev_tokens_possible(rule: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    return [tokens_by_class[_] for _ in rule.get("prev_classes") or []] + [
        set([_]) for _ in rule.get("prev_tokens") or []
    ]


def _curr_and_next_tokens_possible(rule: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    return (
        [set([_]) for _ in rule.get("tokens", [])]
        + [set([_]) for _ in rule.get("next_tokens") or []]
        + [tokens_by_class[_] for _ in rule.get("next_classes") or []]
    )


def _tokens_possible(row: TransliterationRule, tokens_by_class: dict[str, set[str]]) -> list[set[str]]:
    return _prev_tokens_possible(row, tokens_by_class) + _curr_and_next_tokens_possible(row, tokens_by_class)
