from typing import Any

from graphtransliterator.transliterators.bundled import Bundled


class Example(Bundled):
    """
    Example Bundled Graph Transliterator.
    """

    def __init__(
        self, check_ambiguity: bool = False, coverage: bool = False, ignore_errors: bool = False, **kwargs: Any
    ) -> None:
        """Initialize transliterator from YAML or JSON."""
        self.from_bundled_YAML(check_ambiguity=check_ambiguity, coverage=coverage)
