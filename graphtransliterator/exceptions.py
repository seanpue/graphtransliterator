# -*- coding: utf-8 -*-

"""
graphtransliterator.exceptions
------------------------------

Transliteration exceptions used in Graph Transliterator are defined here.
"""


class GraphTransliteratorException(Exception):
    """
    Base exception class. All Graph Transliterator-specific exceptions should
    subclass this class.
    """


class NoMatchingTransliterationRule(GraphTransliteratorException):
    """
    Raised when no transliteration rule can be matched at a particular
    location in the input string's tokens.
    """


class UnrecognizableInputToken(GraphTransliteratorException):
    """
    Raised when a character in the input string does not correspond to any
    tokens in the GraphTranslator's token settings.
    """
