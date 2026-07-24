# -*- coding: utf-8 -*-

# flake8: noqa

"""
graphtransliterator
~~~~~~~~~~~~~~~~~~
"""

__author__ = """A. Sean Pue"""
__email__ = "pue@umd.edu"
__version__ = "1.2.4"

# Core classes
from .core import CoverageTransliterator, GraphTransliterator

# # Constants
# from .compression import (
#     DEFAULT_COMPRESSION_LEVEL,
#     HIGHEST_COMPRESSION_LEVEL,
# )  #  Correct!

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
    # constants
    # "DEFAULT_COMPRESSION_LEVEL",
    # "HIGHEST_COMPRESSION_LEVEL",
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
