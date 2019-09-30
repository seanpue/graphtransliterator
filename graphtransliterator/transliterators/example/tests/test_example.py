# -*- coding: utf-8 -*-
import graphtransliterator.transliterators as transliterators

"""Example tests for transliterator."""
# Generate a Visit-Logging Transliterator`
#  A Bundled object, inherited from CoverageTransliterator and GraphTransliterator
transliterator = transliterators.Example(coverage=True)
# Run YAML tests (in example.yaml)
assert transliterator.run_yaml_tests()
# Check coverage of graph nodes and edges, as well as onmatch rules.
assert transliterator.check_coverage()
