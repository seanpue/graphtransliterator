from collections import OrderedDict
from graphtransliterator.core import GraphTransliterator, CoverageTransliterator
import os
import sys
import yaml


class Bundled(CoverageTransliterator, GraphTransliterator):
    """
    Subclass of GraphTransliterator used for bundled Graph Transliterator.
    """

    @property
    def directory(self):
        """Directory of bundled transliterator, used to load settings."""
        return self._module_dir()

    @property
    def name(self):
        """Name of bundled transliterator, e.g. 'Example'"""
        return self._module_name()

    def _module_dir(self, **kwargs):
        """Returns directory of module. Overwritten during testing."""
        return os.path.dirname(sys.modules[self.__module__].__file__)

    def _module_name(self):
        """Returns name of module. Overwritten during testing."""
        return self.__module__

    def _init_from(self, method=None, **kwargs):
        """Initialize from easy-reading YAML or from JSON."""

        filename = os.path.join(
            self.directory, self.name + "." + method  # error if None
        )
        # Create GraphTransliterator using factory
        if method == "yaml":
            gt = GraphTransliterator.from_yaml_file(filename, **kwargs)
        elif method == "json":
            with open(filename, "r") as f:
                gt = GraphTransliterator.loads(f.read(), **kwargs)
        # Select coverage superclass, if coverage set.
        if kwargs.get("coverage"):
            _super = CoverageTransliterator
        else:
            _super = GraphTransliterator
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
        """Initialize from bundled YAML file (best for development).

        Parameters
        ----------
        check_ambiguity: `bool`,
            Should ambiguity be checked. Default is `True.`
        coverage: `bool`
            Should test coverage be checked. Default is `True`.
        """
        self._init_from(
            method="yaml", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs
        )
        return self

    def from_JSON(self, check_ambiguity=False, coverage=False, **kwargs):
        """Initialize from bundled JSON file (best for speed).

        Parameters
        ----------
        check_ambiguity: `bool`,
            Should ambiguity be checked. Default is `False.`
        coverage: `bool`
            Should test coverage be checked. Default is `False`."""
        self._init_from(
            method="json", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs
        )

    @classmethod
    def new(cls, method="json", **kwargs):
        """Return a new class instance from method (json/yaml).

        Parameters
        ----------
        method: `str` (`json` or `yaml`)
            How to load bundled transliterator, JSON or YAML."""
        assert method in ("json", "yaml"), "Unknown method."
        new_ = cls.__new__(cls)
        if method == "json":
            new_.from_JSON(**kwargs)
        elif method == "yaml":
            new_.from_YAML(**kwargs)
        return new_

    @property
    def yaml_tests_filen(self):
        """
        `dict`: Metadata of transliterator
        """
        return os.path.join(self.directory, "tests", "{}_tests.yaml".format(self.name))

    def load_yaml_tests(self):
        """Iterator for YAML tests.

        Assumes tests are found in subdirectory `tests` of module with name
        `NAME_tests.yaml, e.g. `source_to_target/tests/source_to_target_tests.yaml`.
        """
        test_file = self.yaml_tests_filen
        with open(test_file, "r") as f:
            return {str(k): str(i) for k, i in yaml.safe_load(f).items()}

    def run_tests(self, transliteration_tests):
        """Run transliteration tests.

        Parameters
        ----------
        transliteration_tests: `dict` of {`str`:`str`}
            Dictionary of test from source -> correct target.
        """
        for source, target in transliteration_tests.items():
            source = str(source)
            target = str(target)
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

    def generate_yaml_tests(self, file=None):
        """Generates YAML tests with complete coverage.

        Uses the first token in a class as a sample. Assumes for onmatch rules that
        the first sample token in a class has a unique production, which may not be the
        case. These should be checked and edited."""

        tests = OrderedDict()

        def sample_token(token_class):
            """Return first token in token class."""

            tokens_in_class = self.tokens_by_class[token_class]
            return list(tokens_in_class)[0]

        for rule in self.rules:
            input_ = ""
            if rule.prev_classes:
                for _ in rule.prev_classes:
                    input_ += sample_token(_)
            if rule.prev_tokens:
                for _ in rule.prev_tokens:
                    input_ += _
            for _ in rule.tokens:
                input_ += _
            if rule.next_tokens:
                for _ in rule.next_tokens:
                    input_ += _
            if rule.next_classes:
                for _ in rule.next_classes:
                    input_ += sample_token(_)
            tests[input_] = self.transliterate(input_)

        if self.onmatch_rules:
            for rule in self.onmatch_rules:
                input_ = ""
                for _ in rule.prev_classes:
                    token = sample_token(_)
                    input_ += token
                for _ in rule.prev_classes:
                    token = sample_token(_)
                    input_ += token
                tests[input_] = self.transliterate(input_)

        return yaml.dump(dict(tests), allow_unicode=True)
