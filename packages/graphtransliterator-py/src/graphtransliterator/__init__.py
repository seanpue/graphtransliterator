"""
graphtransliterator
~~~~~~~~~~~~~~~~~~
"""

from importlib.metadata import PackageNotFoundError, version

__author__ = """A. Sean Pue"""
__email__ = "pue@umd.edu"

try:
    __version__ = version("graphtransliterator")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "1.3.3"

# Core classes and functional API
from .core import (
    CoverageTransliterator,
    GraphTransliterator,
    match_at,
    tokenize,
    transliterate,
    transliterate_with_details,
)

# Exceptions
from .exceptions import (
    AmbiguousTransliterationRulesException,
    GraphTransliteratorException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)

# Graphs
from .graphs import DirectedGraph, VisitLoggingDirectedGraph

# Schemas
from .schemas import (
    DirectedGraphSchema,
    EasyReadingSettingsSchema,
    GraphTransliteratorSchema,
    OnMatchRuleSchema,
    SettingsSchema,
    TransliterationRuleSchema,
    WhitespaceDictSettingsSchema,
    WhitespaceSettingsSchema,
)

# Rules
from .types import OnMatchRule, TransliterationRule, WhitespaceRule

__all__ = [
    # Exceptions
    "AmbiguousTransliterationRulesException",
    "CoverageTransliterator",
    # Graphs
    "DirectedGraph",
    "DirectedGraphSchema",
    "EasyReadingSettingsSchema",
    # Core & Functional API
    "GraphTransliterator",
    "GraphTransliteratorException",
    "GraphTransliteratorSchema",
    "NoMatchingTransliterationRuleException",
    "OnMatchRule",
    "OnMatchRuleSchema",
    "SettingsSchema",
    "TransliterationRule",
    "TransliterationRuleSchema",
    "UnrecognizableInputTokenException",
    "VisitLoggingDirectedGraph",
    # Schemas
    "WhitespaceDictSettingsSchema",
    "WhitespaceRule",
    "WhitespaceSettingsSchema",
    "match_at",
    "tokenize",
    "transliterate",
    "transliterate_with_details",
]
