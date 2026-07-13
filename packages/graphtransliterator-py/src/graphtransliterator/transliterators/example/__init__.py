from graphtransliterator.transliterators import Bundled


class Example(Bundled):
    """
    Example Bundled Graph Transliterator.
    """

    def __init__(self, check_ambiguity: bool = False, coverage: bool = False) -> None:
        """Initialize transliterator from YAML or JSON (quicker)."""

        # While testing, initialize from YAML and check ambiguity:

        self.from_JSON(check_ambiguity=check_ambiguity, coverage=coverage)