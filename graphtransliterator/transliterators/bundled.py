# from functools import wraps
# from graphtransliterator.core import # GraphTransliterator, GraphTransliteratorSchema
# from graphtransliterator.graphs import VisitLoggingDirectedGraph
from graphtransliterator.core import GraphTransliterator, CoverageTransliterator

# from graphtransliterator.coverage import CoverageTransliterator
import os
import sys
import yaml


class Bundled(CoverageTransliterator, GraphTransliterator):
    """
    Subclass of GraphTransliterator used by a bundled GraphTransliterator.
    """

    def _init_from(self, method=None, **kwargs):
        """Initialize from easy-reading YAML or from JSON."""
        # Save initialization data in case it becomes a CoverageTransliterator
        # self.yaml_test_file = os.path.join(
        #     os.path.dirname(sys.modules[self.__module__].__file__),
        #     "tests",
        #     self.__module__ + "_tests.yaml",
        # )
        # self.orig_module = self.__module__
        filename = os.path.join(
            os.path.dirname(sys.modules[self.__module__].__file__),
            self.__module__ + "." + method,  # error if None
        )
        # Create GraphTransliterator using factory
        if method == "yaml":
            gt = GraphTransliterator.from_yaml_file(filename, **kwargs)
        elif method == "json":
            with open(filename, "r") as f:
                gt = GraphTransliterator.loads(
                    f.read(), **kwargs
                )  # create GraphTransliterator object
        else:
            raise ValueError("Unknown method")
        #
        # # Select coverage superclass, if coverage set.
        if kwargs.get("coverage"):
            _super = CoverageTransliterator
        else:
            _super = GraphTransliterator
        #
        # # Initialize class using super class's __init__
        # # using created GraphTransliterator's values
        #
        _super.__init__(
            self,
            gt._tokens,
            gt._rules,
            gt._whitespace,
            onmatch_rules=gt._onmatch_rules,
            metadata=gt._metadata,
            ignore_errors=gt._ignore_errors,
            check_ambiguity=kwargs.get("check_ambiguity", False),
            onmatch_rules_lookup=gt._onmatch_rules_lookup,
            tokens_by_class=gt._tokens_by_class,
            graph=gt._graph,
            tokenizer_pattern=gt._tokenizer_pattern,
            graphtransliterator_version=gt._graphtransliterator_version,
            coverage=kwargs.get("coverage", True),
        )

    def from_YAML(self, check_ambiguity=True, coverage=True, **kwargs):
        """Initialize from bundled YAML file (best for development)."""
        self._init_from(
            method="yaml", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs
        )

    def from_JSON(self, check_ambiguity=False, coverage=False, **kwargs):
        """Initialize from bundled JSON file (best for speed)."""
        self._init_from(
            method="json", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs
        )

    #
    # @visitlogging
    # def init_from_bundled_yaml(self, extension=".yaml", **kwargs):
    #     """Return a GraphTransliterator from a bundled easy-reading YAML file."""
    #
    #     yaml_filename = os.path.join(
    #         os.path.dirname(sys.modules[self.__module__].__file__),
    #         self.__module__ + extension
    #     )
    #     import pdb; pdb.set_trace()
    #     gt = self.from_yaml_file(yaml_filename)
    #     self.__init__(gt)
    #     #return cls(gt)   #cls.from_yaml_file(yaml_filename))
    #
    # @classmethod
    # @visitlogging
    # def from_bundled_json(self, path, name, extension=".json", **kwargs):
    #     """Return a GraphTransliterator from a bundled serialized JSON file."""
    #     json_filename = os.path.join(
    #         os.path.dirname(sys.modules[self.__module__].__file__),
    #         self.__module__ + extension
    #     )
    #     with open(json_filename, "r") as f:
    #         json_ = f.read()
    #     return self.load(json_, **kwargs)

    @classmethod
    def load_yaml_tests(self):
        """Iterator for YAML tests.

        Assumes tests are found in subdirectory `tests` of module with name
        `NAME_tests.yaml, e.g. `source_to_target/tests/source_to_target_tests.yaml`.
        """
        test_file = os.path.join(
            os.path.dirname(sys.modules[self.__module__].__file__),
            "tests",
            self.__module__ + "_tests.yaml",
        )
        # test_file = self.yaml_test_file
        with open(test_file, "r") as f:
            return yaml.safe_load(f)

    def run_tests(self, transliteration_tests):
        """Run transliteration tests.

        Parameters
        ----------
        transliteration_tests: `dict` of {`str`:`str`}
            Dictionary of test from source -> correct target.
        """
        for source, target in transliteration_tests.items():
            result = self.transliterate(source)
            assert (
                self.transliterate(source) == target
            ), 'Transliteration error: "{}" -> "{}"; should -> "{}"'.format(
                source, result, target
            )

    def run_yaml_tests(self):
        """Run YAML tests in MODULE/tests/MODULE_tests.yaml"""

        transliteration_tests = self.load_yaml_tests()
        self.run_tests(transliteration_tests)
        return True
