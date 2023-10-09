# -*- coding: utf-8 -*-

# flake8: noqa

"""
graphtransliterator
~~~~~~~~~~~~~~~~~~
Graph Transliterator is a Python module enabling rule-based transliteration
of the tokens of an input string to an output string. It can be used to
transliterate the symbols of one language into those of another, or to
convert between transliteration systems.

:copyright: © 2019 Michigan State University.
:license: MIT, see LICENSE.rst for more details.
"""

__author__ = """A. Sean Pue"""
__email__ = "pue@msu.edu"
__version__ = "1.2.3"

# Core classes
from .core import CoverageTransliterator, GraphTransliterator, GraphTransliteratorSchema

# Constants
from .core import DEFAULT_COMPRESSION_LEVEL, HIGHEST_COMPRESSION_LEVEL

# Exceptions
from .exceptions import (
    GraphTransliteratorException,
    AmbiguousTransliterationRulesException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)

# Graphs
from .graphs import (
    DirectedGraph,
    VisitLoggingDirectedGraph,
    VisitLoggingDict,
    VisitLoggingList,
)

# Rules
from .rules import TransliterationRule, OnMatchRule, WhitespaceRules

# Schemas
from .schemas import (
    DirectedGraphSchema,
    EasyReadingSettingsSchema,
    OnMatchRuleSchema,
    SettingsSchema,
    TransliterationRuleSchema,
    WhitespaceDictSettingsSchema,
    WhitespaceSettingsSchema,
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
    # rules
    "TransliterationRule",
    "OnMatchRule",
    "WhitespaceRules",
    # schemas
    "WhitespaceDictSettingsSchema",
    "WhitespaceSettingsSchema",
    "EasyReadingSettingsSchema",
    "OnMatchRuleSchema",
    "SettingsSchema",
    "TransliterationRuleSchema",
    "DirectedGraphSchema",
]
