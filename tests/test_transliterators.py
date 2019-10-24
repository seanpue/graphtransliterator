# -*- coding: utf-8 -*-
"""Tests for bundled transliterators."""

import pytest
import graphtransliterator.transliterators as transliterators


def _test_bundled_transliterator(transliterator):
    # Confirm transliteratorcan be loaded from yaml (descriptive) and json (faster)
    for method in ("yaml", "json"):

        def init_test_class(self, method=method, coverage=True):
            """Initializes test class. Sets directory and name to superclass's."""
            self._module_dir = transliterator._module_dir
            self._module_name = transliterator._module_name
            self._init_from(method, check_ambiguity=True, coverage=True)

        class_name = "Test{}From{}".format(
            type(transliterator).__name__, method.upper()
        )
        SuperClass = transliterator.__class__
        TestClass = type(class_name, (SuperClass,), {"__init__": init_test_class})
        # Confirm it is a subclass of super class
        assert issubclass(TestClass, SuperClass)
        # Check no coverage works
        assert TestClass(method="json", coverage=False)
        # Create instance of class
        test_class = TestClass(method=method)
        # Load transliteration tests (in tests/test_NAME.yaml)
        transliteration_tests = test_class.load_yaml_tests()
        # Check that bundled tests are in valid format dict {str:str}
        assert type(transliteration_tests) == dict
        for k, v in transliteration_tests.items():
            assert type(k) == str and type(v) == str
        assert len(transliteration_tests) > 0
        # Run yaml tests, calls run_tests()
        test_class.run_yaml_tests()
        # Check there is coverage of graph and onmatch rules in tests
        assert test_class.check_coverage()


def test_bundled_transliterators():
    for transliterator in transliterators.iter_transliterators():
        _test_bundled_transliterator(transliterator)


def test_duplicate_transliterator_error():
    """Test that there can be no transliterators with the same name."""
    with pytest.raises(ValueError):
        transliterators.add_transliterators(path=transliterators.__path__)


def test_iter_names():
    """Test transliterators.iter_names()."""
    assert "Example" in [_ for _ in transliterators.iter_names()]


def test_iter_transliterators():
    """Test transliterators.iter_transliterators()."""
    example = [
        _
        for _ in transliterators.iter_transliterators()
        if type(_).__name__ == "Example"
    ].pop()
    assert example.transliterate("a") == "A"


def test_transliterators_metadata():
    """Confirm that metadata of bundled transliterators matches schema."""
    for _ in transliterators.iter_transliterators():
        assert transliterators.MetadataSchema().load(_.metadata)


def test_bundled():
    """Check that Bundled exists."""
    assert transliterators.Bundled


def test_bundled_new():
    """Test new() function of Bundled."""
    assert transliterators.Example.new(method="json")
    assert transliterators.Example.new(method="yaml")


def test_no_coverage():
    """Test no coverage option."""
    x = transliterators.Example()
    x.from_JSON(coverage=False)
