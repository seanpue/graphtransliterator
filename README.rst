====================
Graph Transliterator
====================


.. image:: https://img.shields.io/pypi/v/graphtransliterator.svg
        :target: https://pypi.python.org/pypi/graphtransliterator

.. image:: https://img.shields.io/travis/seanpue/graphtransliterator.svg
        :target: https://travis-ci.org/seanpue/graphtransliterator

.. image:: https://readthedocs.org/projects/graphtransliterator/badge/?version=latest
        :target: https://graphtransliterator.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/seanpue/graphtransliterator/shield.svg
     :target: https://pyup.io/repos/github/seanpue/graphtransliterator/
     :alt: Updates

A graph-based transliteration tool that lets you convert the symbols of one
language or script to those of another using rules that you define.

Graph Transliterator can be used to:

  * convert language alphabets to transliteration and vice versa
  * convert between transliteration systems
  * convert legacy fonts and encodings into Unicode

* Free software: MIT license
* Documentation: https://graphtransliterator.readthedocs.io.
* Requires: Python 3.5, 3.6, or 3.7

Features
--------

* Provides a transliteration tool that can be configured to convert the tokens
  of an input string into an output string using:

  * definitions of input **tokens** and **token classes**
  * **transliteration rules** based on:

    * a sequence of input tokens
    * specific input tokens that precede or follow the token sequence
    * classes of input tokens preceding or following specific tokens

  * **"on match" rules** for output to be inserted between
    transliteration rules involving particular token classes
  * defined rules for **whitespace**, including its optional consolidation

* Can be setup using:

    * an **"easy reading"** `YAML <https://yaml.org>`_ format that lets you
      quickly craft settings for the transliteration tool
    * **"direct"** settings using a dictionary

* **Automatically orders rules based on specificity** using the number of
  tokens in a transliteration rule
* **Checks for ambiguity** in transliteration rules, where two rules of equal
  specificity could match the same tokens
* Provides **details about each transliteration rule** matched
* Allows **optional matching of all possible rules** in a particular location
* Permits **pruning of rules** with certain productions
* Can be **serialized** as a dictionary for export to JSON, etc.
* Provides **full support for Unicode**, including Unicode **character names**
  in the "easy reading" YAML format
* Constructs and uses a **directed tree** and performs a **best-first search**
  to find the most specific transliteration rule in a given context
