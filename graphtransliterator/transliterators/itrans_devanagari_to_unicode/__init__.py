from graphtransliterator.transliterators import Bundled


class ITRANSDevanagariToUnicode(Bundled):
    """
    ITRANS Devanagari to Unicode Transliterator.
    """

    def __init__(self, **kwargs):
        """Initialize transliterator [from YAML or JSON (quicker)]."""

        # While testing, initialize from YAML and check ambiguity,

        # self.from_YAML(
        #     **kwargs
        # )  # defaults to check_ambiguity=True, check_coverage=True

        # When ready, cut the previous lines and initialize more quickly from JSON:

        self.from_JSON(**kwargs)  # check_ambiguity=False, check_coverage=False
