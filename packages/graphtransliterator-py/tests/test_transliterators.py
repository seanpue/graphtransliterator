# -*- coding: utf-8 -*-
"""Tests for bundled transliterators."""

import pytest

import graphtransliterator.transliterators as transliterators
from graphtransliterator.core import GraphTransliterator
from graphtransliterator.transliterators.bundled import Bundled


def _test_bundled_transliterator(transliterator):
    # Confirm transliterator can be loaded from yaml (descriptive)
    for method in ["yaml"]:  # cut JSON for now

        def init_test_class(self, method=method, coverage=True):
            """Initializes test class. Sets directory and name to superclass's."""
            self._module_dir = transliterator._module_dir
            self._module_name = transliterator._module_name
            self._init_from(method, check_ambiguity=True, coverage=True)

        class_name = "Test{}From{}".format(type(transliterator).__name__, method.upper())
        SuperClass = transliterator.__class__
        TestClass = type(class_name, (SuperClass,), {"__init__": init_test_class})
        # Confirm it is a subclass of super class
        assert issubclass(TestClass, SuperClass)
        # Check no coverage works
        assert TestClass(method="yaml", coverage=False)
        # Create instance of class
        test_class = TestClass(method=method)
        # Load transliteration tests (in tests/test_NAME.yaml)
        transliteration_tests = test_class.load_yaml_tests()
        # Check that bundled tests are in valid format dict {str:str}
        assert isinstance(transliteration_tests, dict)
        for k, v in transliteration_tests.items():
            assert isinstance(k, str) and isinstance(v, str)
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
    example = [_ for _ in transliterators.iter_transliterators() if type(_).__name__ == "Example"].pop()
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
    example_cls = getattr(transliterators, "Example")
    assert example_cls.new(method="yaml")


def test_no_coverage():
    """Test no coverage option."""
    x = transliterators.Example()  # type: ignore
    x.from_bundled_YAML(coverage=False)


def test_bundled_submodules():
    # # Execute top-level imports of sub-packages
    # assert Example is not None
    # assert Itrans_devanagari_to_unicode is not None

    # Iterate over available bundled names
    names = list(transliterators.iter_names())
    assert len(names) > 0
    assert "Example" in names and "ITRANSDevanagariToUnicode" in names
    bundled_transliterators = list(transliterators.iter_transliterators())
    assert len(bundled_transliterators) > 0


def test_bundled_generate_yaml_tests_with_context():
    from graphtransliterator import GraphTransliterator

    gt = GraphTransliterator.from_easyreading_dict(
        {
            "tokens": {"a": ["c1"], "b": ["c2"], "c": ["c3"], " ": ["wb"]},
            "rules": {
                "a": "A",
                "b": "B",
                "c": "C",
                "b (c)": "B_BEFORE_C",
            },
            "onmatch_rules": [{"<c1> + <c2>": "X"}],
            "whitespace": {"default": " ", "consolidate": True, "token_class": "wb"},
        }
    )

    yaml_out = Bundled.generate_yaml_tests(gt)
    assert isinstance(yaml_out, str)
    assert "a" in yaml_out


def test_bundled_module_dir_fallback(monkeypatch):
    class DummyBundled(Bundled):
        pass

    b = DummyBundled.__new__(DummyBundled)

    # Mock sys.modules missing __file__
    monkeypatch.setattr("sys.modules", {b.__module__: None})
    assert b._module_dir() == ""
    assert b._module_name() == b.__module__


def test_bundled_invalid_init_method():
    b = Bundled.__new__(Bundled)
    with pytest.raises(ValueError, match="Method cannot be None"):
        b._init_from(method=None)

    with pytest.raises(ValueError, match="Unknown initialization method"):
        b._init_from(method="invalid_method")


def test_bundled_load_yaml_tests_empty(tmp_path, monkeypatch):
    empty_yaml = tmp_path / "empty_tests.yaml"
    empty_yaml.write_text("")

    class DummyBundled(Bundled):
        @property
        def yaml_tests_filen(self):
            return str(empty_yaml)

    b = DummyBundled.__new__(DummyBundled)
    assert b.load_yaml_tests() == {}


def test_bundled_generate_yaml_tests_full_rules():
    gt = GraphTransliterator.from_easyreading_dict(
        {
            "tokens": {
                "a": ["c1"],
                "b": ["c2"],
                "c": ["c3"],
                " ": ["wb"],
            },
            "rules": {
                "a": "A",
                "b": "B",
                "c": "C",
                "(a) b (c)": "B_IN_CONTEXT",
            },
            "onmatch_rules": [{"<c1> + <c2>": "X"}],
            "whitespace": {"default": " ", "consolidate": True, "token_class": "wb"},
        }
    )

    yaml_str = Bundled.generate_yaml_tests(gt)
    assert "a" in yaml_str
