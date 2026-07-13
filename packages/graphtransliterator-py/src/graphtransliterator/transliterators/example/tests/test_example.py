# -*- coding: utf-8 -*-
import graphtransliterator.transliterators as transliterators

def test_example()-> None:
    """Example tests for transliterator."""
    # Generate a Visit-Logging Transliterator`
    transliterator = transliterators.Example(coverage=True)  # type: ignore[attr-defined]
    # Run YAML tests (in example.yaml)
    assert transliterator.run_yaml_tests()
    # Check coverage of graph nodes and edges, as well as onmatch rules.
    assert transliterator.check_coverage()
