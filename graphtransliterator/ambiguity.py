# -*- coding: utf-8 -*-

"""
GraphTransliterator ambiguity-checking functions.
"""
from .exceptions import AmbiguousTransliterationRulesException
import itertools
import logging


def check_for_ambiguity(transliterator):
    """
    Check if multiple transliteration rules could match the same tokens.

    This function first groups the transliteration rules by number of
    tokens. It then checks to see if any pair of the same cost would match
    the same sequence of tokens. If so, it finally checks if a less costly
    rule would match those particular sequences. If not, there is
    ambiguity.

    Details of all ambiguity are sent in a :func:`logging.warning`.

    Note
    ----
    Called during initialization if ``check_ambiguity`` is set.

    Raises
    ------
    AmbiguousTransliterationRulesException
        Multiple transliteration rules could match the same tokens.

    Example
    -------
    .. jupyter-execute::

      yaml_filename = '''
      tokens:
        a: [class1, class2]
        ' ': [wb]
      rules:
        <class1> a: AW
        <class2> a: AA # ambiguous rule
      whitespace:
        default: ' '
        consolidate: True
        token_class: wb
      '''
      gt = GraphTransliterator.from_yaml(yaml_, check_ambiguity=False)
      gt.check_for_ambiguity()

    """
    ambiguity = False

    all_tokens = set(transliterator._tokens.keys())

    rules = transliterator._rules

    if not rules:
        return True

    max_prev = [_count_of_prev(rule) for rule in rules]
    global_max_prev = max(max_prev)
    max_curr_next = [_count_of_curr_and_next(rule) for rule in rules]
    global_max_curr_next = max(max_curr_next)

    # Generate a matrix of rules, where width is the max of
    # any previous tokens/classes + max of current/next tokens/classes.
    # Each rule's specifications starting from the max of the previous
    # tokens/classes. Other positions are filled by the set of all possible
    # tokens.

    matrix = []

    width = global_max_prev + global_max_curr_next

    for i, rule in enumerate(rules):
        row = [all_tokens] * (global_max_prev - max_prev[i])
        row += _tokens_possible(rule, transliterator._tokens_by_class)
        row += [all_tokens] * (width - len(row))
        matrix += [row]

    def full_intersection(i, j):
        """Intersection of  matrix[i] and matrix[j], else None."""

        intersections = []
        for k in range(width):
            intersection = matrix[i][k].intersection(matrix[j][k])
            if not intersection:
                return None
            intersections += [intersection]
        return intersections

    def covered_by(intersection, row):
        """Check if intersection is covered by row."""
        for i in range(len(intersection)):
            diff = intersection[i].difference(row[i])
            if diff:
                return False
        return True

    # Iterate through rules based on cost (number of tokens). If there are
    # ambiguities, then see if a less costly rule would match the rule. If it does
    # not, there is ambiguity.

    for _group_val, group_iter in itertools.groupby(
        enumerate(transliterator._rules), key=lambda x: x[1].cost
    ):
        group = list(group_iter)
        if len(group) == 1:
            continue
        for i in range(len(group) - 1):
            for j in range(i + 1, len(group)):
                i_index = group[i][0]
                j_index = group[j][0]
                intersection = full_intersection(i_index, j_index)
                if not intersection:
                    break

                # Check if a less costly rule matches intersection

                def covered_by_less_costly():
                    for r_i, rule in enumerate(rules):
                        if r_i in (i_index, j_index):
                            continue
                        if rule.cost > rules[i_index].cost:
                            continue
                        rule_tokens = matrix[r_i]
                        if covered_by(intersection, rule_tokens):
                            return True
                    return False

                if not covered_by_less_costly():
                    logging.warning(
                        "The pattern {} can be matched by both:\n"
                        "  {}\n"
                        "  {}\n".format(
                            intersection,
                            _easyreading_rule(rules[i_index]),
                            _easyreading_rule(rules[j_index]),
                        )
                    )
                    ambiguity = True
    if ambiguity:
        raise AmbiguousTransliterationRulesException


def _easyreading_rule(rule):
    """Get an easy-reading string of a rule."""

    def _token_str(x):
        return " ".join(x)

    def _class_str(x):
        return " ".join(["<%s>" % _ for _ in x])

    out = ""
    if rule.prev_classes and rule.prev_tokens:
        out = "({} {}) ".format(
            _class_str(rule.prev_classes), _token_str(rule.prev_tokens)
        )
    elif rule.prev_classes:
        out = "{} ".format(_class_str(rule.prev_classes))
    elif rule.prev_tokens:
        out = "({}) ".format(_token_str(rule.prev_tokens))

    out += _token_str(rule.tokens)

    if rule.next_tokens and rule.next_classes:
        out += " ({} {})".format(
            _token_str(rule.next_tokens), _class_str(rule.next_classes)
        )
    elif rule.next_tokens:
        out += " ({})".format(_token_str(rule.next_tokens))
    elif rule.next_classes:
        out += " {}".format(_class_str(rule.next_classes))
    return out


def _count_of_prev(rule):
    """Count previous tokens to be present before a match in a rule."""

    return len(rule.prev_classes or []) + len(rule.prev_tokens or [])


def _count_of_curr_and_next(rule):
    """Count tokens to be matched and those to follow them in rule."""

    return len(rule.tokens) + len(rule.next_tokens or []) + len(rule.next_classes or [])


def _prev_tokens_possible(rule, tokens_by_class):
    """`list` of set of possible preceding tokens for a rule."""

    return [tokens_by_class[_] for _ in rule.prev_classes or []] + [
        set([_]) for _ in rule.prev_tokens or []
    ]


def _curr_and_next_tokens_possible(rule, tokens_by_class):
    """`list` of sets of possible current and following tokens for a rule."""

    return (
        [set([_]) for _ in rule.tokens]
        + [set([_]) for _ in rule.next_tokens or []]
        + [tokens_by_class[_] for _ in rule.next_classes or []]
    )


def _tokens_possible(row, tokens_by_class):
    """`list` of sets of possible tokens matched for a rule."""

    return _prev_tokens_possible(row, tokens_by_class) + _curr_and_next_tokens_possible(
        row, tokens_by_class
    )
