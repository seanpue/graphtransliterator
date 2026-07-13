# -*- coding: utf-8 -*-

from graphtransliterator.exceptions import (
    IncompleteGraphCoverageException,
    IncompleteOnMatchRulesCoverageException,
)
import graphtransliterator.transliterators as transliterators
import pytest


def test_CoverageTransliterator():
    """Test coverage using transliterators.Example"""
    # tokens:
    #   a: [vowel]
    #   ' ': [whitespace]
    #   b: [consonant]
    # rules:
    #   a: A
    #   b: B
    #   ' ': ' '
    #   (<consonant> a) b (a <consonant>):  "!B!"
    # -----
    covt = transliterators.Example(coverage=True)
    # unvisited should raise error
    with pytest.raises(IncompleteGraphCoverageException):
        covt.check_coverage()
    # visiting only some nodes should raise error
    with pytest.raises(IncompleteGraphCoverageException):
        assert covt.transliterate("a") == "A"
        assert covt.transliterate("b") == "B"
        covt.check_coverage()
    # visiting all nodes but no onmatch rules should raise error
    with pytest.raises(IncompleteOnMatchRulesCoverageException):
        assert covt.transliterate("a ") == "A "
        assert covt.transliterate("b") == "B"
        assert covt.transliterate("babab") == "BA!B!AB"
        covt.check_coverage()
    # visiting everything should not raise an error
    assert covt.transliterate("aa ") == "A,A "
    assert covt.check_coverage()
    # clearing visited should raise an error when checking coverage
    with pytest.raises(IncompleteGraphCoverageException):
        covt.clear_visited()
        covt.check_coverage()
