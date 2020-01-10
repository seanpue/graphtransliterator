# -*- coding: utf-8 -*-

"""
Tests for ambiguity checking and reporting.
"""

from graphtransliterator import (
    AmbiguousTransliterationRulesException,
    GraphTransliterator, TransliterationRule
)
from graphtransliterator.ambiguity import _easyreading_rule
import pytest


def test_GraphParser_check_ambiguity():
    """ Test for rules that can both match the same thing."""

    yaml_for_test = r"""
        tokens:
          a: [token, class1, class2]
          b: [token, class1, class2]
          ' ': [wb]
        rules:
          a <class1>: A<class1> # these should be ambiguous
          a <class2>: A<class2>

          <class1> a: <class1>A  # these should be ambiguous
          <class2> a: <class2>A # these should be ambiguous

          (<class1> b) a (b <class2>): A # ambigous
          (<class2> b) a (b <class1>): A # ambiguous
          a: A # not ambiguous
        whitespace:
          default: ' '
          token_class: 'wb'
          consolidate: true
        """
    with pytest.raises(AmbiguousTransliterationRulesException):
        GraphTransliterator.from_yaml(yaml_for_test, check_for_ambiguity=True)
    # check that ambiguity matches if rules are of different shape
    yaml = """
        tokens:
          a: []
          ' ': [wb]
        rules:
          <wb> a: _A
          a <wb>: A_
          a: a
          ' ': ' '
        whitespace:
          default: " "        # default whitespace token
          consolidate: true  # whitespace should be consolidated
          token_class: wb     # whitespace token class
        """
    with pytest.raises(AmbiguousTransliterationRulesException):
        GraphTransliterator.from_yaml(yaml, check_for_ambiguity=True)


def test_GraphTransliterator_easy_reading():
    assert (
        _easyreading_rule(
            TransliterationRule("", ["class_a"], [], ["a"], [], ["class_a"], 0)
        )
        == "<class_a> a <class_a>"
    )
    assert (
        _easyreading_rule(
            TransliterationRule("", ["class_a"], [], ["a"], [], ["class_a"], 0)
        )
        == "<class_a> a <class_a>"
    )
    assert (
        _easyreading_rule(TransliterationRule("", [], ["b"], ["a"], ["b"], [], 0))
        == "(b) a (b)"
    )
    assert (
        _easyreading_rule(
            TransliterationRule("", ["class_a"], ["b"], ["a"], ["b"], ["class_a"], 0)
        )
        == "(<class_a> b) a (b <class_a>)"
    )
