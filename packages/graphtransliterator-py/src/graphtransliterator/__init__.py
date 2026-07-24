# -*- coding: utf-8 -*-

# flake8: noqa

# -*- coding: utf-8 -*-

# flake8: noqa

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
    # Fallback for uninstalled local development/testing setups
    __version__ = "1.3.3"

# Core classes
from .core import CoverageTransliterator, GraphTransliterator

# Exceptions
from .exceptions import (
    GraphTransliteratorException,
    AmbiguousTransliterationRulesException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)

# Graphs
from .graphs import DirectedGraph, VisitLoggingDirectedGraph

# Rules
from .types import TransliterationRule, OnMatchRule, WhitespaceRule

# Schemas
from .schemas import (
    DirectedGraphSchema,
    EasyReadingSettingsSchema,
    OnMatchRuleSchema,
    SettingsSchema,
    TransliterationRuleSchema,
    WhitespaceDictSettingsSchema,
    WhitespaceSettingsSchema,
    GraphTransliteratorSchema,  # FIX: Import from .schemas
)

__all__ = [
    # core
    "GraphTransliterator",
    "CoverageTransliterator",
    # exceptions
    "AmbiguousTransliterationRulesException",
    "GraphTransliteratorException",
    "NoMatchingTransliterationRuleException",
    "UnrecognizableInputTokenException",
    # graphs
    "DirectedGraph",
    "VisitLoggingDirectedGraph",
    "TransliterationRule",
    "OnMatchRule",
    "WhitespaceRule",
    # schemas
    "WhitespaceDictSettingsSchema",
    "WhitespaceSettingsSchema",
    "EasyReadingSettingsSchema",
    "OnMatchRuleSchema",
    "SettingsSchema",
    "TransliterationRuleSchema",
    "DirectedGraphSchema",
    "GraphTransliteratorSchema",
]
