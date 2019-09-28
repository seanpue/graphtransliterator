from graphtransliterator.transliterators import Bundled


class Example(Bundled):
    """
    Example Bundled Graph Transliterator
    """

    def __init__(self, **kwargs):
        """Initializes transliterator from YAML or JSON (quicker)."""

        # While testing, initialize from YAML and check ambiguity.

        self.from_YAML(
            **kwargs
        )  # defaults to check_ambiguity=True, check_coverage=True

        # When set, cut the previous line and initialize more quickly from JSON

        # self.init_from_JSON() # check_ambiguity=False, check_coverage=False
