====================
Graph Transliterator
====================

.. image:: https://img.shields.io/pypi/v/graphtransliterator.svg
      :target: https://pypi.python.org/pypi/graphtransliterator
      :alt: PyPi Version

.. image:: https://readthedocs.org/projects/graphtransliterator/badge/?version=latest
      :target: https://graphtransliterator.readthedocs.io/en/latest/?badge=latest
      :alt: Documentation Status

.. image:: https://pyup.io/repos/github/seanpue/graphtransliterator/shield.svg
     :target: https://pyup.io/repos/github/seanpue/graphtransliterator/
     :alt: PyUp Updates

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Code Style: Black

.. image:: https://img.shields.io/pypi/pyversions/graphtransliterator
     :alt: PyPI - Python Version

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3558365.svg
     :target: https://doi.org/10.5281/zenodo.3558365
     :alt: Software repository DOI

.. image:: https://joss.theoj.org/papers/10.21105/joss.01717/status.svg
     :target: https://doi.org/10.21105/joss.01717
     :alt: Paper DOI

A graph-based transliteration tool that lets you convert the symbols of one
language or script to those of another using rules that you define.

* Free software: MIT license
* Documentation: https://graphtransliterator.readthedocs.io
* Repository: https://github.com/seanpue/graphtransliterator

Transliteration... What? Why?
-----------------------------

Moving text or data from one script or encoding to another is a common problem:

- Many languages are written in multiple scripts, and many people can only read one of
  them. Moving between them can be a complex but necessary task in order to make
  texts accessible.

- The identification of names and locations, as well as machine translation,
  benefit from transliteration.

- Library systems often require metadata be in particular forms of romanization in
  addition to the original script.

- Linguists need to move between different methods of phonetic transcription.

- Documents in legacy fonts must now be converted to contemporary Unicode ones.

- Complex-script languages are frequently approached in natural language processing and
  in digital humanities research through transliteration, as it provides disambiguating
  information about pronunciation, morphological boundaries, and unwritten elements not
  present in the original script.

Graph Transliterator abstracts transliteration, offering an "easy reading" method for
developing transliterators that does not require writing a complex program. It also
contains bundled transliterators that are rigorously tested. These can be expanded to
handle many transliteration tasks.

Contributions are very welcome!


Features
--------

* Provides a transliteration tool that can be configured to convert the tokens
  of an input string into an output string using:

  * user-defined types of input **tokens** and **token classes**
  * **transliteration rules** based on:

    * a sequence of input tokens
    * specific input tokens that precede or follow the token sequence
    * classes of input tokens preceding or following specified tokens

  * **"on match" rules** for output to be inserted between transliteration
    rules involving particular token classes
  * defined rules for **whitespace**, including its optional consolidation

* Can be setup using:

  * an **"easy reading"** `YAML <https://yaml.org>`_ format that lets you
    quickly craft settings for the transliteration tool
  * a `JSON <https://json.org>`_ dump of a transliterator (quicker!)
  * **"direct"** settings, perhaps passed programmatically, using a dictionary

* **Automatically orders rules** by the number of tokens in a
  transliteration rule
* **Checks for ambiguity** in transliteration rules
* Can provide **details** about each transliteration rule match
* Allows **optional matching of all possible rules** in a particular location
* Permits **pruning of rules** with certain productions
* **Validates**, as well as **serializes** to and **deserializes** from JSON
  and Python data types, using accessible
  `marshmallow <https://marshmallow.readthedocs.io/>`_ schemas
* Provides **full support for Unicode**, including Unicode **character names**
  in the "easy reading" YAML format
* Constructs and uses a **directed tree** and performs a **best-first search**
  to find the most specific transliteration rule in a given context
* Includes **bundled transliterators** that *you* can add to
  hat check for full test coverage of the nodes and edges of the internal graph and any
  "on match" rules
* Includes a command-line interface to perform transliteration and other tasks

Sample Code and Graph
---------------------

.. code-block:: python

  from graphtransliterator import GraphTransliterator
  GraphTransliterator.from_yaml("""
      tokens:
        h: [consonant]
        i: [vowel]
        " ": [whitespace]
      rules:
        h: \N{LATIN SMALL LETTER TURNED I}
        i: \N{LATIN SMALL LETTER TURNED H}
        <whitespace> i: \N{LATIN CAPITAL LETTER TURNED H}
        (<whitespace> h) i: \N{LATIN SMALL LETTER TURNED H}!
      onmatch_rules:
        - <whitespace> + <consonant>: ¡
      whitespace:
        default: " "
        consolidate: true
        token_class: whitespace
      metadata:
        title: "Upside Down Greeting Transliterator"
        version: "1.0.0"
  """).transliterate("hi")

.. code-block:: python

    '¡ᴉɥ!'

.. figure:: https://raw.githubusercontent.com/seanpue/graphtransliterator/master/docs/_static/sample_graph.png
   :alt: sample graph

   Sample directed tree created by Graph Transliterator. The `rule` nodes are in double
   circles, and `token` nodes  are single circles. The numbers are the cost of the
   particular edge, and less costly edges are searched first. Previous token classes
   and previous tokens that must be present are found as constraints on the edges
   incident to the terminal leaf `rule` nodes.


Get It Now
==========

.. code-block:: bash

   $ pip install -U graphtransliterator

Citation
========

To cite Graph Transliterator, please use:

    Pue, A. Sean (2019). Graph Transliterator: A graph-based transliteration tool.
    Journal of Open Source Software, 4(44), 1717, https://doi.org/10.21105/joss.01717
