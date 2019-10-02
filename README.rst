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

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black

.. image:: https://img.shields.io/pypi/pyversions/graphtransliterator
       :alt: PyPI - Python Version

A graph-based transliteration tool that lets you convert the symbols of one
language or script to those of another using rules that you define.


* Free software: MIT license
* Documentation: https://graphtransliterator.readthedocs.io.


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
* Includes **bundled transliterators** that can be add to and that check for full
  test coverage of the nodes and edges of the internal graph and any "on match" rules

Sample Code and Graph
---------------------

.. code-block:: python
  :linenos:

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

.. code-block:: none

  '¡ᴉɥ!'

.. figure:: https://raw.githubusercontent.com/seanpue/graphtransliterator/master/docs/_static/sample_graph.png
   :alt: sample graph

   Sample directed tree created by Graph Transliterator. The `rule` nodes are in double circles,
   and `token` nodes  are single circles. The numbers are the cost of the particular
   edge, and less costly edges are searched first. Previous token class
   (``prev_classes``) and previous token (``prev_tokens``) constraints
   are found on edges before leaf rule nodes.
