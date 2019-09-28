# -*- coding: utf-8 -*-
import pytest

"""Tests for bundled transliterators."""

# from graphtransliterator.exceptions import IncompleteGraphCoverageException
# from graphtransliterator.transliterators import Bundled
import graphtransliterator.transliterators as transliterators

# from io import StringIO
# import pytest
# import yaml
import pdb

pdb.set_trace()
transliterator = transliterators.Example()  # Load example bundled transliterator

#
# def test_coverage_exception():
#     """Because all edges and nodes have been visited, there should be an exception.
#
#     This function can be cut from tests, but is given here as an example."""
#     with pytest.raises(IncompleteGraphCoverageException):
#         transliterator.graph.check_coverage()
#
#
# def test_clear_coverage():
#     """Test clearing of visit history."""
#     transliterator.graph.clear_visited()
#     with pytest.raises(IncompleteGraphCoverageException):
#         transliterator.graph.check_coverage()
#
#     transliterator.transliterate("a ")  # run all rules
#     assert transliterator.graph.check_coverage()
#
#     transliterator.graph.clear_visited()
#     with pytest.raises(IncompleteGraphCoverageException):
#         transliterator.graph.check_coverage()

#
# # Define transliteration tests
#
# # These should be a dictionary from source to correct target:
# transliteration_tests = {"a": "A", " ": " "}
#
# # These can also come from a YAML string:
# transliteration_tests = yaml.safe_load(
#     StringIO(
#         """
#         a: A
#         ' ': ' '
#         """
#     )
# )
# # Or use the `Bundled` class to load
# import pdb; pdb.set_trace()
# transliteration_tests = transliterator.load_yaml_tests()
#
# print(transliteration_tests)
#


def test_transliterator():
    """Write tests here to confirm the transliterator works correctly.

    All nodes, edges, and onmatch_rules should be visited."""

    transliterator.run_yaml_tests()


def test_duplicate_transliterator():
    """Test that there can be no transliterators with the same name."""
    with pytest.raises(ValueError):
        transliterators.add_transliterators(path=transliterators.__path__)


def test_iter_names():
    """Test transliterators.iter_names()"""
    assert "Example" in [_ for _ in transliterators.iter_names()]


def test_iter_transliterators():
    """Test transliteratorss.iter_transliterators()"""
    import pdb

    pdb.set_trace()
    example = [
        _
        for _ in transliterators.iter_transliterators()
        if type(_).__name__ == "Example"
    ].pop()
    assert example.transliterate("a") == "A"


def test_bundled():
    # check that Bundled exists
    assert transliterators.Bundled


def test_all_transliterators():
    import pdb

    pdb.set_trace()
    for transliterator in transliterators.iter_transliterators():
        import pdb

        pdb.set_trace()
        test_class = type(transliterator.__class__)

        x = temp_class().from_YAML(coverage=True)
        # x = transliterator.from_YAML(coverage=True)
        #
        # assert transliterator.from_JSON(coverage=True)
        # pass


# Iterate through transliteration


#
#     for source, target in transliteration_tests.items():
#         result = transliterator.transliterate(source)
#         assert (
#             transliterator.transliterate(source) == target
#         ), 'Transliteration error: "{}" -> "{}"; should -> "{}"'.format(
#             source, result, target
#         )
#     # Finally, test coverage — were all nodes and edges of the graph visited?
#     # We are all onmatch_rules used?
#
#     transliterator.graph.check_coverage()
#
#

#
# def test_json_load(tmpdir):
#     """Test JSON load."""
#     import pdb; pdb.set_trace()
#     assert transliterators.Example.init_from_JSON().transliterate('a') == 'A'
#     # f = tmpdir.mkdir("sub").join("hello.txt")
#     # f.write(transliterator.dump())
#     # import pdb;pdb.set_trace()
#     # assert Bundled.init_from_JSON(str(f)).transliterate("a") == "A"
