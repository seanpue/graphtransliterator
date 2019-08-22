#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `graphtransliterator` package."""
import graphtransliterator
import pytest
import re
import yaml
from graphtransliterator import GraphTransliterator
from graphtransliterator.core import _easyreading_rule
from graphtransliterator import process
from graphtransliterator.rules import OnMatchRule, TransliterationRule, WhitespaceRules
from graphtransliterator.graphs import DirectedGraph

from graphtransliterator.exceptions import (
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
    AmbiguousTransliterationRulesException,
)
from marshmallow import ValidationError

yaml_for_test = r"""
tokens:
  a: [token, class1]
  b: [token, class2]
  u: [token]
  ' ': [wb]
rules:
  a: A
  b: B
  <wb> u: \N{DEVANAGARI LETTER U}
onmatch_rules:
  -
    <class1> + <class2>: ","
  -
    <class1> + <token>: \N{DEVANAGARI SIGN VIRAMA}
whitespace:
  default: ' '
  token_class: 'wb'
  consolidate: true
metadata:
  author: Author Name
"""


def test_GraphTransliterator_from_YAML():
    """Test YAML loading of GraphTransliterator."""
    good_yaml = """
      tokens:
        a: [class1]
        ' ': [wb]
      rules:
        a: A
      whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """
    assert GraphTransliterator.from_yaml(good_yaml)
    bad_yaml = """
      tokens:
        a: class1
        ' ': wb
      rules:
        a: A
      whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    bad_yaml = """
      tokens:
        a: class1
        ' ': wb
      rules:
        a: A
      whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """
    # tokens values are not lists
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    bad_yaml = """
          rules:
            a: A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)
    bad_yaml = """
          rules:
            a: A
          tokens:
            a: [token]
            ' ': [wb]
          whitespace:
            default: 'BAD'
            consolidate: true
            token_class: bad
    """
    # whitespace errors
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)
    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)
    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            a: A
    """
    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            b: A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            (b) a: A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            a (b): A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    bad_yaml = """
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            a <class_nonexisting>: A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)

    # test for bad tokens
    bad_yaml = """
          tokens: '7'
          rules:
            a <class_nonexisting>: A
          whitespace:
            default: ' '
            consolidate: true
            token_class: wb
    """
    with pytest.raises(ValidationError):
        GraphTransliterator.from_yaml(bad_yaml)


def test_graphtransliterator_process():
    """Test graphtransliterator proccessing of rules."""

    data = yaml.safe_load(yaml_for_test)

    assert process._process_rules({"a": "A"})[0]["tokens"] == ["a"]
    assert process._process_rules({"a": "A"})[0]["production"] == "A"
    assert (
        process._process_onmatch_rules(data["onmatch_rules"])[0]["prev_classes"][0]
        == "class1"
    )
    assert (
        process._process_onmatch_rules(data["onmatch_rules"])[0]["next_classes"][0]
        == "class2"
    )


def test_graphtransliterator_models():
    """Test internal models."""
    tr = TransliterationRule(
        production="A",
        prev_classes=None,
        prev_tokens=None,
        tokens=["a"],
        next_tokens=None,
        next_classes=None,
        cost=1,
    )
    assert tr.cost == 1
    # assert TransliteratorOutput([tr], 'A').output == 'A'
    assert OnMatchRule(prev_classes=["class1"], next_classes=["class2"], production=",")
    assert WhitespaceRules(default=" ", token_class="wb", consolidate=False)


def test_graphtransliterator_structures():
    graph = DirectedGraph()

    assert len(graph.node) == 0
    assert len(graph.edge) == 0

    graph.add_node({"type": "test1"})
    graph.add_node({"type": "test2"})
    assert graph.node[0]["type"] == "test1"
    assert graph.node[1]["type"] == "test2"

    graph.add_edge(0, 1, {"type": "edge_test1"})
    assert graph.edge[0][1]["type"] == "edge_test1"
    assert type(graph.to_dict()) == dict

    # edge tail not in graph
    with pytest.raises(ValueError):
        graph.add_edge(0, 7, {})
    # edge head not in graph
    with pytest.raises(ValueError):
        graph.add_edge(7, 0, {})

    # invalid edge data
    with pytest.raises(ValueError):
        graph.add_edge(0, 1, "not a dict")

    # invalid edge head type
    with pytest.raises(ValueError):
        graph.add_edge("zero", 1)
    # invalid edge tail type
    with pytest.raises(ValueError):
        graph.add_edge(1, "zero")
    # invalid node data
    with pytest.raises(ValueError):
        graph.add_node("Not a dict")


# def test_graphtransliterator_validate_settings():
#     """Test graph transliterator validation of settings."""
#     settings = yaml.safe_load(yaml_for_test)
#     # check for bad tokens
#     settings["tokens"] = "bad token"
#     with pytest.raises(marshmallow.ValidationError):
#         validate.validate_settings(
#             settings["tokens"],
#             settings["rules"],
#             settings["onmatch_rules"],
#             settings["whitespace"],
#             {},
#         )


def test_GraphTransliterator_transliterate(tmpdir):
    """Test GraphTransliterator transliterate."""
    YAML = r"""
    tokens:
        a: [class_a]
        b: [class_b]
        c: [class_c]
        " ": [wb]
        d: []
        Aa: [contrained_rule]
    rules:
        a: A
        b: B
        <class_c> <class_c> a: A(AFTER_CLASS_C_AND_CLASS_C)
        (<class_c> b) a: A(AFTER_B_AND_CLASS_C)
        (<class_c> b b) a a: AA(AFTER_BB_AND_CLASS_C)
        a <class_c>: A(BEFORE_CLASS_C)
        a b (c <class_b>): AB(BEFORE_C_AND_CLASS_B)
        c: C
        c c: C*2
        a (b b b): A(BEFORE_B_B_B)
        d (c <class_a>): D(BEFORE_C_AND_CLASS_A)
        (b b) a: A(AFTER_B_B)
        <wb> Aa: A(ONLY_A_CONSTRAINED_RULE)
    onmatch_rules:
        -
            <class_a> <class_b> + <class_a> <class_b>: "!"
        -
            <class_a> + <class_b>: ","
    whitespace:
        default: ' '
        consolidate: True
        token_class: wb
    """
    gt = GraphTransliterator.from_yaml(YAML)
    # rules with single token
    assert gt.transliterate("a") == "A"
    # rules with multiple tokens
    assert gt.transliterate("aa") == "AA"
    # rules with multiple tokens (for rule_key)
    assert gt.transliterate("cc") == "C*2"
    # # rules with multiple tokens overlapping end of tokens
    # assert gt.transliterate('c') == 'C'

    # rules with prev class
    assert gt.transliterate("ca") == "CA"
    # rules with prev class and prev token
    assert gt.transliterate("dca") == "D(BEFORE_C_AND_CLASS_A)CA"
    # rules with prev class and prev tokens
    assert gt.transliterate("cbba") == "CBBA(AFTER_B_B)"
    # rules with next class
    assert gt.transliterate("ac") == "A(BEFORE_CLASS_C)C"
    # rules with next class and next tokens
    assert gt.transliterate("acb") == "A(BEFORE_CLASS_C)CB"
    # rules with onmatch rule of length 1
    assert gt.transliterate("ab") == "A,B"
    # rules that only have constraints on first element
    assert gt.transliterate("Aa") == "A(ONLY_A_CONSTRAINED_RULE)"
    # test whitespace consolidation
    assert gt.transliterate(" a") == "A"
    # test whitespace consolidation following
    assert gt.transliterate("a ") == "A"

    # rules with longer onmatch rules
    assert gt.transliterate("abab") == "A,B!A,B"

    # test last_matched_input_tokens
    assert gt.last_input_tokens == [" ", "a", "b", "a", "b", " "]
    # test last_matched_tokens
    assert gt.last_matched_rule_tokens == [["a"], ["b"], ["a"], ["b"]]

    # test last_matched_rules
    assert len(gt.last_matched_rules) == 4

    # test dump
    assert gt.dump()["graph"]["edge"]
    assert type(GraphTransliterator.load(gt.dump())) == GraphTransliterator
    assert "graph" in gt.dumps()
    assert re.match(r"\d+\.\d+\.\d+$", gt.dump()["graphtransliterator_version"])
    assert gt.dump()["graphtransliterator_version"] == graphtransliterator.__version__
    x = gt.dumps()
    assert type(x) == str
    new_gt = GraphTransliterator.loads(x)
    assert type(new_gt) == GraphTransliterator


def test_version():
    """Tests to make sure version is not a mess due to Black formatting"""

    assert re.match(r"\d+\.\d+\.\d+$", graphtransliterator.__version__)


def test_match_all():
    """Test GraphTransliterator transliterate."""
    YAML = r"""
    tokens:
        a: [class_a]
        " ": [wb]
    rules:
        a: A
        a a: A*2
    whitespace:
        default: ' '
        consolidate: True
        token_class: wb
    """
    gt = GraphTransliterator.from_yaml(YAML)
    assert gt.rules[0].cost < gt.rules[1].cost

    tokens = gt.tokenize("aa")
    assert gt.match_at(1, tokens, match_all=False) == 0
    assert gt.match_at(1, tokens, match_all=True) == [0, 1]


def test_GraphTransliterator(tmpdir):
    """Test GraphTransliterator."""
    yaml_str = r"""
    tokens:
      a: [token, class1]
      b: [token, class2]
      u: [token]
      ' ': [wb]
    rules:
      a: A
      b: B
      <wb> u: \N{DEVANAGARI LETTER U}
    onmatch_rules:
      -
        <class1> + <class2>: ","
      -
        <class1> + <token>: \N{DEVANAGARI SIGN VIRAMA}
    whitespace:
      default: ' '
      token_class: 'wb'
      consolidate: true
    metadata:
      author: Author
    """

    input_dict = yaml.safe_load(yaml_str)
    assert "a" in GraphTransliterator.from_easyreading_dict(input_dict).tokens.keys()
    gt = GraphTransliterator.from_easyreading_dict(input_dict)
    assert gt.onmatch_rules[0].production == ","
    assert gt.tokens
    assert gt.rules
    assert gt.whitespace
    assert gt.whitespace.default
    assert gt.whitespace.token_class
    assert gt.whitespace.consolidate
    assert gt.metadata["author"] == "Author"
    assert type(gt.graph) == DirectedGraph
    yaml_file = tmpdir.join("yaml_test.yaml")
    yaml_filename = str(yaml_file)
    yaml_file.write(yaml_str)

    assert yaml_file.read() == yaml_str

    assert GraphTransliterator.from_yaml_file(yaml_filename)

    assert len(set(GraphTransliterator.from_easyreading_dict(input_dict).tokens)) == 4

    assert GraphTransliterator.from_yaml(yaml_str).transliterate("ab") == "A,B"
    assert (
        GraphTransliterator.from_yaml_file(yaml_filename).transliterate("ab") == "A,B"
    )
    assert (
        GraphTransliterator.from_easyreading_dict(
            {
                "tokens": {"a": ["class_a"], "b": ["class_b"], " ": ["wb"]},
                "onmatch_rules": [{"<class_a> + <class_b>": ","}],
                "whitespace": {
                    "default": " ",
                    "token_class": "wb",
                    "consolidate": True,
                },
                "rules": {"a": "A", "b": "B"},
            }
        ).transliterate("ab")
        == "A,B"
    )


def test_GraphTransliterator_ignore_errors():
    # if ignore_errors is not set and no matching transliteration rule
    # raise NoMatchingTransliterationRule exception
    yaml_str = """
        tokens:
           a: [class1]
           b: [class1]
           ' ': [wb]
        rules:
           a a: B2
           b: B
        whitespace:
           default: ' '
           consolidate: true
           token_class: wb
           """
    # check that ignore_errors works
    assert (
        GraphTransliterator.from_yaml(yaml_str, ignore_errors=True).transliterate("a")
        == ""
    )

    with pytest.raises(NoMatchingTransliterationRuleException):
        gt = GraphTransliterator.from_yaml(yaml_str, ignore_errors=False)
        assert gt.ignore_errors is False
        gt.transliterate("a")

    with pytest.raises(UnrecognizableInputTokenException):
        gt = GraphTransliterator.from_yaml(yaml_str, ignore_errors=False)
        assert gt.ignore_errors is False
        gt.transliterate("!")

    gt = GraphTransliterator.from_yaml(yaml_str, ignore_errors=True)
    assert gt.ignore_errors is True
    assert gt.tokenize("b!b") == [" ", "b", "b", " "]
    assert gt.transliterate("b!b") == "BB"

    with pytest.raises(UnrecognizableInputTokenException):
        gt = GraphTransliterator.from_yaml(yaml_str, ignore_errors=False)
        assert gt.ignore_errors is False
        gt.transliterate("b!")

    # # test ignore_errors keyword value checking on init
    # with pytest.raises(ValueError):
    #     GraphTransliterator.from_yaml(yaml_str, ignore_errors="maybe")
    # test ignore_errors keyword property

    # test ignore_errors setter and property
    gt.ignore_errors = True
    assert gt.ignore_errors is True
    gt.ignore_errors = False
    assert gt.ignore_errors is False
    # test ignore_errors setter exception handling
    # with pytest.raises(ValueError):
    #     gt.ignore_errors = "Maybe"


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


def test_GraphTransliterator_types():
    """Test internal types."""
    pr = TransliterationRule(
        production="A",
        prev_classes=None,
        prev_tokens=None,
        tokens=["a"],
        next_tokens=None,
        next_classes=None,
        cost=1,
    )
    assert pr.cost == 1
    #    assert TransliteratorOutput([pr], 'A').output == 'A'
    assert OnMatchRule(prev_classes=["class1"], next_classes=["class2"], production=",")
    assert WhitespaceRules(default=" ", token_class="wb", consolidate=False)

    graph = DirectedGraph()

    assert len(graph.node) == 0
    assert len(graph.edge) == 0

    graph.add_node({"type": "test1"})
    graph.add_node({"type": "test2"})
    assert graph.node[0]["type"] == "test1"
    assert graph.node[1]["type"] == "test2"

    graph.add_edge(0, 1, {"type": "edge_test1"})
    assert graph.edge[0][1]["type"] == "edge_test1"


def test_GraphTransliterator_productions():
    """Test productions."""
    tokens = {"ab": ["class_ab"], " ": ["wb"]}
    whitespace = {"default": " ", "token_class": "wb", "consolidate": True}
    rules = {"ab": "AB", " ": "_"}
    settings = {"tokens": tokens, "rules": rules, "whitespace": whitespace}
    assert set(GraphTransliterator.from_easyreading_dict(settings).productions) == set(
        ["AB", "_"]
    )


def test_GraphTransliterator_pruned_of():
    gt = GraphTransliterator.from_yaml(
        """
            tokens:
               a: [class1]
               b: [class2]
               ' ': [wb]
            rules:
               a: A
               b: B
            whitespace:
               default: ' '
               consolidate: true
               token_class: wb
        """
    )
    assert len(gt.rules) == 2
    assert len(gt.pruned_of("B").rules) == 1
    assert gt.pruned_of("B").rules[0].production == "A"
    assert gt.pruned_of(["A", "B"])  # if no rules present will still work


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


def test_GraphTransliterator_graph():
    """Test graph."""
    tokens = {"ab": ["class_ab"], " ": ["wb"]}
    whitespace = {"default": " ", "token_class": "wb", "consolidate": True}
    rules = {"ab": "AB", " ": "_"}
    settings = {"tokens": tokens, "rules": rules, "whitespace": whitespace}
    gt = GraphTransliterator.from_easyreading_dict(settings)
    assert gt._graph
    assert gt._graph.node[0]["type"] == "Start"  # test for Start
    assert gt
