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
__email__ = 'pue@msu.edu'
__version__ = '0.2.6'

# Core classes
from .core import GraphTransliterator  # noqa

# Graphs
from .graphs import DirectedGraph # noqa

# Rules
from .rules import (TransliterationRule, OnMatchRule, WhitespaceRules) # noqa

# Exceptions
from .exceptions import (
    GraphTransliteratorException,
    AmbiguousTransliterationRulesException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException
) # noqa

from .validate import (
    validate_easyreading_settings,
    validate_settings
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
    # validate
    "validate_easyreading_settings",
    "validate_settings"

]
