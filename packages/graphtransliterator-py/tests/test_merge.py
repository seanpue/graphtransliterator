# -*- coding: utf-8 -*-
import pytest
from graphtransliterator import GraphTransliterator


def test_graph_transliterator_merge_success():
    """Verify that two valid transliterators combine their rules and tokens seamlessly."""
    setup1 = {
        "tokens": {"a": ["A_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["a"], "production": "alpha"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
        "metadata": {"author": "Alice"},
    }
    gt1 = GraphTransliterator.from_dict(setup1)

    setup2 = {
        "tokens": {"b": ["B_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["b"], "production": "beta"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
        "metadata": {"version": "2.0"},
    }
    gt2 = GraphTransliterator.from_dict(setup2)

    # Perform the merge operation via the method
    merged_gt = gt1.merge(gt2)

    # Assert rules, tokens, and metadata are combined
    assert len(merged_gt.rules) == 2
    assert "a" in merged_gt.tokens
    assert "b" in merged_gt.tokens
    assert merged_gt.metadata == {"author": "Alice", "version": "2.0"}

    # Verify runtime behavior of both profiles
    assert merged_gt.transliterate("a") == "alpha"
    assert merged_gt.transliterate("b") == "beta"


def test_graph_transliterator_add_operator():
    """Verify that using the '+' operator achieves identical results to calling .merge()."""
    setup1 = {
        "tokens": {"a": ["A_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["a"], "production": "alpha"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
    }
    gt1 = GraphTransliterator.from_dict(setup1)

    setup2 = {
        "tokens": {"b": ["B_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["b"], "production": "beta"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
    }
    gt2 = GraphTransliterator.from_dict(setup2)

    # Use the operator override
    added_gt = gt1 + gt2

    assert len(added_gt.rules) == 2
    # Transliterate concatenated string without unhandled intermediate space tokens
    assert added_gt.transliterate("ab") == "alphabeta"

    # Ensure adding an incompatible type returns NotImplemented or raises a TypeError
    with pytest.raises(TypeError):
        gt1 + "not a transliterator instance"


def test_graph_transliterator_merge_whitespace_mismatch():
    """Verify that merging throws a ValueError if whitespace settings differ."""
    setup1 = {
        "tokens": {"a": ["A_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["a"], "production": "alpha"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
    }
    gt1 = GraphTransliterator.from_dict(setup1)

    setup2 = {
        "tokens": {"b": ["B_CLASS"], "_": ["WS"]},
        "rules": [{"tokens": ["b"], "production": "beta"}],
        "whitespace": {"default": "_", "token_class": "WS", "consolidate": False},
    }
    gt2 = GraphTransliterator.from_dict(setup2)

    with pytest.raises(ValueError, match="Configuration Mismatch"):
        gt1.merge(gt2)


def test_graph_transliterator_merge_onmatch_rules():
    """Verify that contextual onmatch rules merge cleanly."""
    setup1 = {
        "tokens": {"a": ["A_CLASS"], "b": ["B_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["a"], "production": "alpha"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
        "onmatch_rules": [
            {
                "prev_classes": ["B_CLASS"],
                "next_classes": ["A_CLASS"],
                "production": "special_a",
            }
        ],
    }
    gt1 = GraphTransliterator.from_dict(setup1)

    setup2 = {
        "tokens": {"b": ["B_CLASS"], " ": ["WS"]},
        "rules": [{"tokens": ["b"], "production": "beta"}],
        "whitespace": {"default": " ", "token_class": "WS", "consolidate": True},
    }
    gt2 = GraphTransliterator.from_dict(setup2)

    merged = gt1 + gt2
    assert merged.onmatch_rules is not None
    assert len(merged.onmatch_rules) == 1
