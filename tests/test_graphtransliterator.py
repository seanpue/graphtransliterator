#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `graphtransliterator` package."""
# from click.testing import CliRunner
from graphtransliterator import process
from graphtransliterator.core import GraphTransliterator
from graphtransliterator.exceptions import (
    IncorrectVersionException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)
from graphtransliterator.graphs import DirectedGraph
from graphtransliterator.rules import OnMatchRule, TransliterationRule, WhitespaceRules
from itertools import combinations
from marshmallow import ValidationError
import graphtransliterator
import pytest
import re
import yaml

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
    # test graph
    graph = DirectedGraph()

    assert len(graph.node) == 0
    assert len(graph.edge) == 0
    # test with node data
    graph.add_node({"type": "test1"})
    graph.add_node({"type": "test2"})
    assert graph.node[0]["type"] == "test1"
    assert graph.node[1]["type"] == "test2"
    # test if no node data
    graph.add_node()  # 2
    # test add_edge
    graph.add_edge(0, 1, {"type": "edge_test1"})
    assert graph.edge[0][1]["type"] == "edge_test1"
    # test add_edge with no edge data
    graph.add_edge(1, 2)
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
    # test edge_list
    assert len(graph.edge_list) > 1
    # test create graph without node, edges but not edge_list ads edge_list
    assert DirectedGraph(node=graph.node, edge=graph.edge).edge_list == graph.edge_list


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


def test_serialization():
    """Test serialization of graphtransliterator"""
    # Field definitions
    required_fields = ["tokens", "rules", "whitespace"]
    optional_fields = [
        "onmatch_rules",
        "metadata",
        "ignore_errors",
        "onmatch_rules_lookup",
        "tokens_by_class",
        "graph",
        "tokenizer_pattern",
        "graphtransliterator_version",
    ]
    ordered_fields = required_fields + optional_fields
    yaml_ = """
        tokens:
          a: [vowel]
          ' ': [wb]
        rules:
          a: A
          ' ': ' '
        whitespace:
          default: " "
          consolidate: false
          token_class: wb
        onmatch_rules:
          - <vowel> + <vowel>: ','  # add a comma between vowels
        metadata:
          author: "Author McAuthorson"
    """
    gt = GraphTransliterator.from_yaml(yaml_)
    # test dump
    dump = gt.dump()
    assert dump["graph"]["edge"]
    # test ordering of dump fields
    assert list(dump.keys()) == ordered_fields
    # test dump version
    assert dump["graphtransliterator_version"] == graphtransliterator.__version__
    assert re.match(r"\d+\.\d+\.\d+$", gt.dump()["graphtransliterator_version"])
    # test dumps
    x = gt.dumps()
    assert "graph" in gt.dumps()
    assert type(x) == str
    # test loads
    new_gt = GraphTransliterator.loads(x)
    assert GraphTransliterator.loads(gt.dumps()).dumps()
    assert type(new_gt) == GraphTransliterator
    # test load
    settings = gt.dump()
    assert type(GraphTransliterator.load(settings)) == GraphTransliterator
    # confirm settings not affected by load
    assert settings == settings
    # confirm compacting (dropping) optional settings works
    for length in range(1, len(optional_fields)):
        for to_drop in combinations(optional_fields, length):
            settings = gt.dump()
            for _ in to_drop:
                settings.pop(_)
            if settings.get("onmatch_rules_lookup") and not settings.get(
                "onmatch_rules"
            ):
                with pytest.raises(ValidationError):
                    assert GraphTransliterator.load(settings)
            else:
                assert GraphTransliterator.load(settings)
    # test IncorrectVersionException
    _ = gt.dump()
    _['graphtransliterator_version'] += "1"  # add 1 e.g. 1.0.11
    with pytest.raises(IncorrectVersionException):
        assert GraphTransliterator.load(_)


def test_version():
    """Tests to make sure version is not a mess (e.g. due to Black formatting)"""

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

    # test ignore_errors setter and property
    gt.ignore_errors = True
    assert gt.ignore_errors is True
    gt.ignore_errors = False
    assert gt.ignore_errors is False


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
