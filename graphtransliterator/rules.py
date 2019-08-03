# -*- coding: utf-8 -*-

"""
Graph Transliterator rule classes.
"""

from collections import namedtuple


class TransliterationRule(
    namedtuple(
        "TransliterationRule",
        [
            "production",
            "prev_classes",
            "prev_tokens",
            "tokens",
            "next_tokens",
            "next_classes",
            "cost",
        ],
    )
):
    """
    A transliteration rule containing the specific match conditions and
    string output to be produced, as well as the rule's cost.

    Attributes
    ----------
    production: `str`
        Output produced on match of rule
    prev_classes: `list` of `str`, or `None`
        List of previous token classes to be matched before tokens or,
        if they exist, `prev_tokens`
    prev_tokens: `list` of `str`, or `None`
        List of tokens to be matched before `tokens`
    tokens: `list` of `str`
        List of tokens to match
    next_tokens: `list` of `str`, or `None`
        List of tokens to match after `tokens`
    next_classes: `list` of `str`, or `None`
        List of tokens to match after `tokens` or, if they exist, `next_tokens`
    cost: `float`
        Cost of the rule, where less specific rules are more costly
    """

    __slots__ = ()


class OnMatchRule(
    namedtuple("OnMatchRule", ["prev_classes", "next_classes", "production"])
):
    """
    Rules about adding text between certain combinations of matched rules.

    When a translation rule has been found and before its production is added
    to the output, the productions string of an OnMatch rule is added if
    previously matched tokens and current tokens are of the specified classes.

    Attributes
    ----------
    prev_classes: `list` of `str`
        List of previously matched token classes required
    next_classes: `list` of `str`
        List of current and following token classes required
    production: `str`
        String to added before current rule
    """

    __slots__ = ()


class WhitespaceRules(
    namedtuple("Whitespace", ["default", "token_class", "consolidate"])
):
    """
    Whitespace rules of GraphTransliterator.

    Attributes
    ----------
    default: `str`
        Default whitespace token
    token_class: `str`
        Whitespace token class
    consolidate: `bool`
        Consolidate consecutive whitespace tokens and render as a single
        instance of the specified default whitespace token.
    """

    __slots__ = ()
