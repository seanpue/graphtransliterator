# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import sys
from typing import Any, Dict, Iterator, Optional, Type, Union, cast, TYPE_CHECKING
import yaml

from graphtransliterator.core import GraphTransliterator, CoverageTransliterator
from graphtransliterator.compression import DEFAULT_COMPRESSION_LEVEL, HIGHEST_COMPRESSION_LEVEL

class Bundled(CoverageTransliterator, GraphTransliterator):
    """
    Subclass of GraphTransliterator used for bundled Graph Transliterator.
    """

    @property
    def directory(self) -> str:
        """Directory of bundled transliterator, used to load settings."""
        return self._module_dir()

    @property
    def name(self) -> str:
        """Name of bundled transliterator, e.g. 'Example'"""
        return self._module_name()

    def _module_dir(self, **kwargs: Any) -> str:
        """Returns directory of module. Overwritten during testing."""
        module = sys.modules[self.__module__]
        if module and hasattr(module, "__file__") and module.__file__:
            return os.path.dirname(module.__file__)
        return ""

    def _module_name(self) -> str:
        """Returns name of module. Overwritten during testing."""
        return self.__module__

    def _init_from(self, method: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize from easy-reading YAML or from JSON."""
        if method is None:
            raise ValueError("Method cannot be None")

        filename = os.path.join(
            self.directory,
            self.name + "." + method,
        )
        
        # Create GraphTransliterator using factory
        if method == "yaml":
            gt = GraphTransliterator.from_yaml_file(filename, **kwargs)
        elif method == "json":
            with open(filename, "r", encoding="utf-8") as f:
                gt = GraphTransliterator.loads(f.read(), **kwargs)
        else:
            raise ValueError(f"Unknown initialization method: {method}")

        # Select coverage superclass, if coverage set.
        _super: Type[Union[CoverageTransliterator, GraphTransliterator]] = (
            CoverageTransliterator if kwargs.get("coverage") else GraphTransliterator
        )
        
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

    def from_YAML(self, check_ambiguity: bool = True, coverage: bool = True, **kwargs: Any) -> "Bundled":
        """Initialize from bundled YAML file (best for development)."""
        self._init_from(method="yaml", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs)
        return self

    def from_JSON(self, check_ambiguity: bool = False, coverage: bool = False, **kwargs: Any) -> "Bundled":
        """Initialize from bundled JSON file (best for speed)."""
        self._init_from(method="json", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs)
        return self

    @classmethod
    def new(cls, method: str = "json", **kwargs: Any) -> "Bundled":
        """Return a new class instance from method (json/yaml)."""
        assert method in ("json", "yaml"), "Unknown method."
        new_ = cast("Bundled", cls.__new__(cls))
        if method == "json":
            new_.from_JSON(**kwargs)
        elif method == "yaml":
            new_.from_YAML(**kwargs)
        return new_

    @property
    def yaml_tests_filen(self) -> str:
        """
        `str`: Absolute path to the bundled YAML test file.
        """
        return os.path.join(self.directory, "tests", "{}_tests.yaml".format(self.name))

    def load_yaml_tests(self) -> Dict[str, str]:
        """Iterator for YAML tests."""
        test_file = self.yaml_tests_filen
        with open(test_file, "r", encoding="utf-8") as f:
            parsed_yaml = yaml.safe_load(f)
            if not parsed_yaml:
                return {}
            return {str(k): str(i) for k, i in parsed_yaml.items()}

    def run_tests(self, transliteration_tests: Dict[str, str]) -> None:
        """Run transliteration tests."""
        for source, target in transliteration_tests.items():
            source = str(source)
            target = str(target)
            result = self.transliterate(source)
            assert result == target, 'Transliteration error: "{}" -> "{}"; should -> "{}"'.format(
                source, result, target
            )

    def run_yaml_tests(self) -> bool:
        """Run YAML tests in MODULE/tests/MODULE_tests.yaml"""
        transliteration_tests = self.load_yaml_tests()
        self.run_tests(transliteration_tests)
        return True

    def generate_yaml_tests(self, file: Optional[Any] = None) -> str:
        """Generates YAML tests with complete coverage."""
        tests: OrderedDict[str, str] = OrderedDict()

        def sample_token(token_class: str) -> str:
            """Return first token in token class."""
            tokens_in_class = self.tokens_by_class[token_class]
            return str(list(tokens_in_class)[0])

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
            for om_rule in self.onmatch_rules:
                input_ = ""
                if om_rule.prev_classes:
                    for _ in om_rule.prev_classes:
                        token = sample_token(_)
                        input_ += token
                    for _ in om_rule.prev_classes:
                        token = sample_token(_)
                        input_ += token
                tests[input_] = self.transliterate(input_)

        return cast(str, yaml.dump(dict(tests), allow_unicode=True))