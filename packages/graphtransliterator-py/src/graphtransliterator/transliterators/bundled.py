# -*- coding: utf-8 -*-

import os
import sys
from collections import OrderedDict
from typing import Any, Dict, Iterable, Optional, cast

import yaml

from graphtransliterator.core import CoverageTransliterator, GraphTransliterator


class Bundled(CoverageTransliterator, GraphTransliterator):
    """Subclass of GraphTransliterator used for bundled Graph Transliterators."""

    @property
    def directory(self) -> str:
        """Directory of bundled transliterator, used to load settings."""
        return self._module_dir()

    @property
    def name(self) -> str:
        """Name of bundled transliterator, e.g. 'Example'"""
        return self._module_name().split(".")[-1]

    def _module_dir(self, **kwargs: Any) -> str:
        """Returns directory of module. Overwritten during testing."""
        module = sys.modules.get(self.__module__)
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
            f"{self.name}.{method}",
        )

        if method == "yaml":
            gt = GraphTransliterator.from_yaml_file(filename, **kwargs)
        elif method == "json":
            with open(filename, "r", encoding="utf-8") as f:
                gt = GraphTransliterator.loads(f.read(), **kwargs)
        else:
            raise ValueError(f"Unknown initialization method: {method}")

        super().__init__(
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

    def from_bundled_YAML(self, check_ambiguity: bool = True, coverage: bool = True, **kwargs: Any) -> "Bundled":
        """Initialize from bundled YAML file (best for development)."""
        self._init_from(method="yaml", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs)
        return self

    def from_bundled_JSON(self, check_ambiguity: bool = False, coverage: bool = False, **kwargs: Any) -> "Bundled":
        """Initialize from bundled JSON file (best for speed)."""
        self._init_from(method="json", check_ambiguity=check_ambiguity, coverage=coverage, **kwargs)
        return self

    @classmethod
    def new(cls, method: str = "yaml", **kwargs: Any) -> "Bundled":
        """Return a new class instance from method (json/yaml)."""
        if method not in ("json", "yaml"):
            raise ValueError(f"Unknown method '{method}'. Expected 'json' or 'yaml'.")

        new_ = cast("Bundled", cls.__new__(cls))
        if method == "json":
            new_.from_bundled_JSON(**kwargs)
        else:
            new_.from_bundled_YAML(**kwargs)
        return new_

    @property
    def yaml_tests_filen(self) -> str:
        """str: Absolute path to the bundled YAML test file."""
        return os.path.join(self.directory, "tests", f"{self.name}_tests.yaml")

    def load_yaml_tests(self) -> Dict[str, str]:
        """Load YAML tests mapping."""
        test_file = self.yaml_tests_filen
        if not os.path.exists(test_file):
            return {}

        with open(test_file, "r", encoding="utf-8") as f:
            parsed_yaml = yaml.safe_load(f)
            if not parsed_yaml:
                return {}
            return {str(k): str(v) for k, v in parsed_yaml.items()}

    def run_tests(self, transliteration_tests: Dict[str, str]) -> None:
        """Run transliteration tests."""
        for source, target in transliteration_tests.items():
            result = self.transliterate(str(source))
            assert result == str(target), f'Transliteration error: "{source}" -> "{result}"; should -> "{target}"'

    def run_yaml_tests(self) -> bool:
        """Run YAML tests in MODULE/tests/MODULE_tests.yaml."""
        transliteration_tests = self.load_yaml_tests()
        self.run_tests(transliteration_tests)
        return True

    def generate_yaml_tests(self, file: Optional[Any] = None) -> str:
        """Generates YAML tests with complete coverage."""
        tests: OrderedDict[str, str] = OrderedDict()

        def sample_token(token_class: str) -> str:
            """Return first token in token class."""
            tokens_in_class: Iterable[str] = self.tokens_by_class.get(token_class, [])
            return str(next(iter(tokens_in_class), ""))

        for rule in self.rules:
            input_ = ""
            for cls_name in rule.get("prev_classes") or []:
                input_ += sample_token(cls_name)
            for tok in rule.get("prev_tokens") or []:
                input_ += tok
            for tok in rule.get("tokens") or []:
                input_ += tok
            for tok in rule.get("next_tokens") or []:
                input_ += tok
            for cls_name in rule.get("next_classes") or []:
                input_ += sample_token(cls_name)

            if input_:
                tests[input_] = self.transliterate(input_)

        if self.onmatch_rules:
            for om_rule in self.onmatch_rules:
                input_ = ""
                for cls_name in om_rule.get("prev_classes") or []:
                    input_ += sample_token(cls_name)
                for cls_name in om_rule.get("next_classes") or []:
                    input_ += sample_token(cls_name)

                if input_:
                    tests[input_] = self.transliterate(input_)

        dumped = yaml.dump(dict(tests), allow_unicode=True)
        if file is not None:
            if hasattr(file, "write"):
                file.write(dumped)
            else:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(dumped)

        return cast(str, dumped)
