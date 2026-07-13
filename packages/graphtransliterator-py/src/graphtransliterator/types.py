# -*- coding: utf-8 -*-
"""
Centralized domain types for GraphTransliterator.
"""

from typing import Any
from typing_extensions import TypeAlias, TypedDict, NotRequired

# Simple Domain Semantics
Token: TypeAlias = str
TokenClass: TypeAlias = str


# Raw Configuration Formats
class RawRuleDict(TypedDict, total=False):
    """Shape of a raw dictionary representing a transliteration rule."""

    production: str
    prev_classes: list[TokenClass] | None
    prev_tokens: list[Token] | None
    tokens: list[Token]
    next_tokens: list[Token] | None
    next_classes: list[TokenClass] | None
    cost: float


class RawOnMatchDict(TypedDict):
    """Shape of a raw dictionary representing an on-match rule."""

    prev_classes: list[TokenClass]
    next_classes: list[TokenClass]
    production: str


class RawWhitespaceDict(TypedDict):
    """Shape of a raw dictionary representing whitespace rules."""

    default: Token
    token_class: TokenClass
    consolidate: bool


# Structural Domain Semantics
class ConstraintDict(TypedDict):
    prev_classes: NotRequired[list[TokenClass]]
    prev_tokens: NotRequired[list[Token]]
    next_tokens: NotRequired[list[Token]]
    next_classes: NotRequired[list[TokenClass]]


class EdgeData(TypedDict):
    token: NotRequired[Token]
    cost: float
    constraints: NotRequired[ConstraintDict]


class NodeData(TypedDict):
    token: NotRequired[Token]
    type: NotRequired[str]
    ordered_children: NotRequired[dict[str, Any]]
    accepting: NotRequired[bool]
    rule_key: NotRequired[int]


class LoadedGraphDict(TypedDict):
    node: list[NodeData]
    edge: dict[int, dict[int, EdgeData]]
    edge_list: list[tuple[int, int]]
