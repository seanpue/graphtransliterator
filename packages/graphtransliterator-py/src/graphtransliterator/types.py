"""
Centralized domain types for GraphTransliterator.
"""

from typing import Any, Generic, TypeAlias, TypeVar

from typing_extensions import NotRequired, TypedDict

ConstraintDict: TypeAlias = dict[str, Any]
LoadedSettingsDict: TypeAlias = dict[str, Any]

# Generic types used for DirectedGraph typing in core.py
GTNodeType: TypeAlias = str
GTNodeDataType: TypeAlias = dict[str, Any]
GTEdgeDataType: TypeAlias = dict[str, Any]


# =============================================================================
# DOMAIN PRIMITIVES & IDENTIFIERS
# =============================================================================

Token: TypeAlias = str
TokenClass: TypeAlias = str
NodeId: TypeAlias = int
NodeLabel: TypeAlias = str
RuleId: TypeAlias = int
OnMatchRuleId: TypeAlias = int

# Generic Parameters (Parity with TS Node<T, N> and Edge<E>)
T = TypeVar("T")  # Node type discriminant
N = TypeVar("N")  # Node payload data type
E = TypeVar("E")  # Edge payload data type

# =============================================================================
# GENERIC GRAPH PARITY INTERFACES (Shared 1:1 with TypeScript)
# =============================================================================


class Node(TypedDict, Generic[T, N]):
    """Generic vertex representation matching TS Node<T, N>."""

    id: NodeId
    token: Token | None
    type: T
    label: NodeLabel | None
    data: N


class Edge(TypedDict, Generic[E]):
    """Generic edge representation matching TS Edge<E>."""

    source: NodeId
    target: NodeId
    data: E


class LoadedGraphDict(TypedDict, Generic[T, N, E]):
    """Canonical JSON serialization shape shared with TypeScript."""

    nodes: list[Node[T, N]]
    edges: list[Edge[E]]


# =============================================================================
# RULE DECLARATIONS (Converted from NamedTuples -> TypedDicts)
# =============================================================================


class TransliterationRule(TypedDict):
    """A transliteration rule containing match conditions and cost."""

    production: str
    tokens: list[Token]
    cost: float
    prev_classes: NotRequired[list[TokenClass] | None]
    prev_tokens: NotRequired[list[Token] | None]
    next_tokens: NotRequired[list[Token] | None]
    next_classes: NotRequired[list[TokenClass] | None]


class OnMatchRule(TypedDict):
    """Rule adding text between specific combinations of matched rules."""

    prev_classes: list[TokenClass]
    next_classes: list[TokenClass]
    production: str


class WhitespaceRule(TypedDict):
    """Whitespace rule definition (renamed from WhitespaceRule for 1:1 parity)."""

    default: Token
    token_class: TokenClass
    consolidate: bool


# =============================================================================
# RAW SCHEMA CONFIGURATION INTERFACES
# =============================================================================


class RawRuleDict(TypedDict, total=False):
    """Shape of an unparsed raw dictionary representing a transliteration rule."""

    production: str
    prev_classes: list[TokenClass] | None
    prev_tokens: list[Token] | None
    tokens: list[Token]
    next_tokens: list[Token] | None
    next_classes: list[TokenClass] | None
    cost: float | None


class RawOnMatchDict(TypedDict):
    """Shape of an unparsed raw dictionary representing an on-match rule."""

    prev_classes: list[TokenClass]
    next_classes: list[TokenClass]
    production: str


class RawWhitespaceDict(TypedDict):
    """Shape of an unparsed raw dictionary representing whitespace rules."""

    default: Token
    token_class: TokenClass
    consolidate: bool


class EasyReadingDict(TypedDict):
    """Explicit type layout representing an Easy Reading configuration dictionary."""

    tokens: dict[Token, list[TokenClass]]
    rules: dict[str, str]
    whitespace: RawWhitespaceDict
    onmatch_rules: NotRequired[list[dict[str, str]]]
    metadata: NotRequired[dict[str, Any]]
