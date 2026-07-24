# Graph Transliterator Workspace

[![PyPI Version](https://img.shields.io/pypi/v/graphtransliterator.svg)](https://pypi.python.org/pypi/graphtransliterator)
[![npm version](https://img.shields.io/npm/v/graphtransliterator.svg)](https://www.npmjs.com/package/graphtransliterator)
[![Documentation Status](https://readthedocs.org/projects/graphtransliterator/badge/?version=latest)](https://graphtransliterator.readthedocs.io/en/latest/?badge=latest)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphtransliterator)](https://pypi.org/project/graphtransliterator/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3558365.svg)](https://doi.org/10.5281/zenodo.3558365)
[![Paper DOI](https://joss.theoj.org/papers/10.21105/joss.01717/status.svg)](https://doi.org/10.21105/joss.01717)

A graph-based transliteration framework that converts symbols from one language or script to another using customizable rules.

This repository is a monorepo containing both the **Python** and **TypeScript / JavaScript** implementations of Graph Transliterator.

* **Free software:** MIT license
* **Documentation:** [graphtransliterator.readthedocs.io](https://graphtransliterator.readthedocs.io)
* **Repository:** [github.com/seanpue/graphtransliterator](https://github.com/seanpue/graphtransliterator)

---

## Transliteration... What? Why?

Moving text or data from one script or encoding to another is a common problem:

* Many languages are written in multiple scripts, and many people can only read one of them.
* Name identification, location mapping, and machine translation benefit from transliteration.
* Library systems frequently require metadata in specific forms of romanization alongside original scripts.
* Linguists shift between different phonetic transcription methods.
* Legacy font documents need conversion to modern Unicode formats.
* Complex-script languages in NLP and digital humanities rely on transliteration to disambiguate pronunciation, morphological boundaries, and unwritten elements.

Graph Transliterator abstracts this process by offering an "easy reading" format (using YAML/JSON) for building transliterators without writing complex parsing programs.

---

## ✨ Features

* **Flexible Token & Rule Definitions:** Define input tokens, token classes, and lookahead/lookbehind context rules.
* **Contextual "On Match" Rules:** Insert production tokens when specific token classes adjoin.
* **Whitespace Management:** Configure default whitespace tokens and whitespace consolidation.
* **Easy Configuration:** Set up via YAML ("easy reading"), direct dictionary/JSON, or loaded settings.
* **Automatic Cost Ordering:** Rules automatically order based on match length (longest match preferred).
* **Ambiguity Checking:** Detects overlapping rules of equal cost during graph initialization.
* **Unicode Support:** Native support for Unicode character escapes and names (e.g., `\N{LATIN SMALL LETTER TURNED I}`).
* **Directed Graph Engine:** Builds an internal directed tree and runs a best-first search.
* **Dual Language Ecosystem:** Complete native implementations for both **Python** and **TypeScript/JavaScript**.

---

## 💡 Quick Example (Python)

```python
from graphtransliterator import GraphTransliterator

gt = GraphTransliterator.from_yaml("""
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
""")

print(gt.transliterate("hi"))  # Output: '¡ᴉɥ!'
