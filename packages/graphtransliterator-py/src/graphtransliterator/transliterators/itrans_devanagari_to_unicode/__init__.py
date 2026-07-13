# -*- coding: utf-8 -*-

from graphtransliterator.transliterators import Bundled


class ITRANSDevanagariToUnicode(Bundled):
    """
    ITRANS Devanagari to Unicode Transliterator.
    """

    def __init__(self, check_ambiguity: bool = False, coverage: bool = False) -> None:
        """Initialize transliterator [from YAML or JSON (quicker)]."""

        # While testing, initialize from YAML and check ambiguity,

        # self.from_YAML(
        #     check_ambiguity=check_ambiguity, coverage=coverage
        # )  # defaults to check_ambiguity=True, check_coverage=True

        # When ready, cut the previous lines and initialize more quickly from JSON:

        self.from_JSON(check_ambiguity=check_ambiguity, coverage=coverage)
