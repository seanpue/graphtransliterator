"""
Tests for ambiguity checking and reporting.
"""

import pytest
from graphtransliterator import (
    AmbiguousTransliterationRulesException,
    GraphTransliterator,
)
from graphtransliterator.ambiguity import _easyreading_rule, check_for_ambiguity


def test_GraphParser_check_ambiguity():
    """Test for rules that can both match the same thing."""

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
            {
                "production": "",
                "prev_classes": ["class_a"],
                "prev_tokens": [],
                "tokens": ["a"],
                "next_tokens": [],
                "next_classes": ["class_a"],
                "cost": 0.0,
            }
        )
        == "<class_a> a <class_a>"
    )
    assert (
        _easyreading_rule(
            {
                "production": "",
                "prev_classes": ["class_a"],
                "prev_tokens": [],
                "tokens": ["a"],
                "next_tokens": [],
                "next_classes": ["class_a"],
                "cost": 0.0,
            }
        )
        == "<class_a> a <class_a>"
    )
    assert (
        _easyreading_rule(
            {
                "production": "",
                "prev_classes": [],
                "prev_tokens": ["b"],
                "tokens": ["a"],
                "next_tokens": ["b"],
                "next_classes": [],
                "cost": 0.0,
            }
        )
        == "(b) a (b)"
    )
    assert (
        _easyreading_rule(
            {
                "production": "",
                "prev_classes": ["class_a"],
                "prev_tokens": ["b"],
                "tokens": ["a"],
                "next_tokens": ["b"],
                "next_classes": ["class_a"],
                "cost": 0.0,
            }
        )
        == "(<class_a> b) a (b <class_a>)"
    )


class DummyTransliterator:
    _tokens = {}
    _rules = []
    _tokens_by_class = {}


def test_check_ambiguity_empty_rules():
    assert check_for_ambiguity(DummyTransliterator()) is True


def test_ambiguity_empty_rules_and_explicit_cost():
    class DummyEmptyTransliterator:
        _tokens = {}
        _rules = []
        _tokens_by_class = {}

    assert check_for_ambiguity(DummyEmptyTransliterator()) is True
