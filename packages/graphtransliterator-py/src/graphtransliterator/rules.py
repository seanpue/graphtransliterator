# -*- coding: utf-8 -*-

"""
Graph Transliterator rule classes.
"""

from typing import NamedTuple
from .types import Token, TokenClass


class TransliterationRule(NamedTuple):
    """
    A transliteration rule containing the specific match conditions and
    string output to be produced, as well as the rule's cost.
    """

    production: str
    prev_classes: list[TokenClass] | None
    prev_tokens: list[Token] | None
    tokens: list[Token]
    next_tokens: list[Token] | None
    next_classes: list[TokenClass] | None
    cost: float


class OnMatchRule(NamedTuple):
    """
    Rules about adding text between certain combinations of matched rules.
    """

    prev_classes: list[TokenClass]
    next_classes: list[TokenClass]
    production: str


class WhitespaceRules(NamedTuple):
    """
    Whitespace rules of GraphTransliterator.
    """

    default: Token
    token_class: TokenClass
    consolidate: bool