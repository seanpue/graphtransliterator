# -*- coding: utf-8 -*-

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
__version__ = "0.3.8"

# Core classes
from .core import GraphTransliterator, GraphTransliteratorSchema  # noqa

# Exceptions
from .exceptions import (
    GraphTransliteratorException,
    AmbiguousTransliterationRulesException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)  # noqa

# Graphs
from .graphs import DirectedGraph  # noqa

# Rules
from .rules import TransliterationRule, OnMatchRule, WhitespaceRules  # noqa

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
    # exceptions
    "AmbiguousTransliterationRulesException",
    "GraphTransliteratorException",
    "NoMatchingTransliterationRuleException",
    "UnrecognizableInputTokenException",
    # graphs
    "DirectedGraph",
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
