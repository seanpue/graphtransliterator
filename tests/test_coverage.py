# -*- coding: utf-8 -*-

# from graphtransliterator.coverage import CoverageTransliterator
from graphtransliterator.exceptions import (
    IncompleteGraphCoverageException,
    IncompleteOnMatchRulesCoverageException,
)
import graphtransliterator.transliterators as transliterators
import pytest


def test_CoverageTransliterator():
    """Test coverage using transliterators.Example"""
    # YAML:
    # ------
    # tokens:
    #   a: [vowel]
    #   ' ': [whitespace]
    # rules:
    #   a: A
    #   ' ': ' '
    # onmatch_rules:
    #   - <vowel> + <vowel>: ","
    # whitespace:
    #   consolidate: False
    #   default: " "
    #   token_class: whitespace
    # -----
    covt = transliterators.Example(coverage=True)
    # unvisited should raise error
    with pytest.raises(IncompleteGraphCoverageException):
        covt.check_coverage()
    # visiting only some nodes should raise error
    with pytest.raises(IncompleteGraphCoverageException):
        assert covt.transliterate("a") == "A"
        covt.check_coverage()
    # visiting all nodes but no onmatch rules should raise error
    with pytest.raises(IncompleteOnMatchRulesCoverageException):
        assert covt.transliterate("a ") == "A "
        covt.check_coverage()
    # visiting everything should not raise an error
    assert covt.transliterate("aa ") == "A,A "
    assert covt.check_coverage()
    # clearing visited should raise an error when checking coverage
    with pytest.raises(IncompleteGraphCoverageException):
        covt.clear_visited()
        covt.check_coverage()
    # visiting all nodes but not using all onmatch rules should raise an error
    with pytest.raises(IncompleteOnMatchRulesCoverageException):
        assert covt.transliterate("a ") == "A "
        covt.check_coverage()
