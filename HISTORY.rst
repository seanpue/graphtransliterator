=======
History
=======

[Unreleased - Maybe]
--------------------
* Add CLI
* Add metadata guidelines
* Save match location in tokenize
* Add tests directly to YAML files
* Allow insertion of transliteration error messages into output
* Fix Devanagari output in Sphinx-generated Latex PDF
* Add translated messages using Transifex
* Add examples module
* add `compact` flag to remove null values from dump and dumps

[Unreleased-TODO]
-----------------

0.3.5 (2019-09-15)
------------------
* flake8 fix for core.py
* fixed bug in schemas.py whereby, during load(), DirectedGraphSchema() was modifying
  input settings
* added tests for modifications to settings by load()
* adjusted DirectedGraphSchema to allow for compacted transliteration rule settings
* adjusted GraphTransliteratorSchema to allow for compacted settings
* added tests to confirm all optional fields passed to load() are really optional
* added ValidationError if onmatch_rules_lookup present without onmatch_rules
* adjusted DirectedGraphSchema edge definition to remove str if loading from JSON
* added more rigorous schema definitions for edge_list and node in DirectedGraphSchema
* fixed flake8 warning in graphs.py
* adjusted docstrings in core.py for dump(), dumps(), load(), and loads()

0.3.4 (2019-09-15)
------------------
* added sphinx-issues and settings to requirements_dev.txt, docs/conf.py
* added .readthedocs.yml configuration file to accommodate sphinx-issues
* removed history from setup.py due to sphinx-issues
* fixed GraphTransliteratorException import in __init__.py
* added docs/_static directory
* fixed emphasis error and duplicate object description in docs/usages.rst
* fixed docstring in core.py
* added python versions badge to README.rst (:issue:`openjournals/joss-reviews#1717`).
  Thanks :user:`vc1492a`.
* added NOTICE listing licenses of open-source text and code
* added Dependencies information to docs/install.rst
  (:issue:`openjournals/joss-reviews#1717`). Thanks :user:`vc1492a`.
* updated AUTHORS.rst
* minor updates to README.rst

0.3.3 (2019-09-14)
------------------
* fixed missing marshmallow dependency (:pr:`47`). Thanks :user:`vc1492a`.
* removed unused code from test (:pr:`47`). Thanks :user:`vc1492a`.
* removed cerberus dependency

0.3.2 (2019-08-30)
------------------
* fixed error in README.rst

0.3.1 (2019-08-29)
------------------
* adjustments to README.rst
* cleanup in initialize.py and core.py
* fix to docs/api.rst
* adjusted setup.cfg for bumpversion of core.py
* adjusted requirements.txt
* removed note about namedtuple in dump docs
* adjusted docs (api.rst, etc.)

0.3.0 (2019-08-23)
-------------------
* Removed _tokens_of() from init
* Removed serialize()
* Added load() to GraphTransliterator, without ambiguity checking
* Added dump() and dumps() to GraphTransliterator to export configuration
* renamed _tokenizer_from() to _tokenizer_pattern_from(), and so that regex is compiled
  on load and passed as pattern string (tokenizer_pattern)
* added settings parameters to DirectedGraph
* added OnMatchRule as namedtuple for consistency
* added new GraphTransliterator.from_dict(), which validates from_yaml()
* renamed GraphTransliterator.from_dict() to GraphTransliterator.from_easyreading_dict()
* added schemas.py
* removed validate.py
* removed cerberus and added marshmallow to validate.py
* adjusted tests
* Removed check_settings parameter

0.2.14 (2019-08-15)
-------------------
* minor code cleanup
* removed yaml from validate.py

0.2.13 (2019-08-03)
-------------------
* changed setup.cfg for double quotes in bumpversion due to Black formatting of setup.py
* added version test

0.2.12 (2019-08-03)
-------------------
* fixed version error in setup.py

0.2.11 (2019-08-03)
-------------------
* travis issue

0.2.10 (2019-08-03)
-------------------
* fixed test for version not working on travis

0.2.9 (2019-08-03)
------------------
* Used Black code formatter
* Adjusted tox.ini, contributing.rst
* Set development status to Beta in setup.py
* Added black badge to README.rst
* Fixed comments and minor changes in initialize.py

0.2.8 (2019-07-30)
------------------
* Fixed ambiguity check if no rules present
* Updates to README.rst

0.2.7 (2019-07-28)
-----------------------
* Modified docs/conf.py
* Modified equation in docs/usage.rst and paper/paper.md to fix doc build

0.2.6 (2019-07-28)
------------------
* Fixes to README.rst, usage.rst, paper.md, and tutorial.rst
* Modifications to core.py documentation

0.2.5 (2019-07-24)
------------------
* Fixes to HISTORY.rst and README.rst
* 100% test coverage.
* Added draft of paper.
* Added graphtransliterator_version to serialize().

0.2.4 (2019-07-23)
------------------
* minor changes to readme

0.2.3 (2019-07-23)
------------------
* added xenial to travis.yml

0.2.2 (2019-07-23)
------------------
* added CI

0.2.1 (2019-07-23)
------------------
* fixed HISTORY.rst for PyPI

0.2.0 (2019-07-23)
------------------
* Fixed  module naming in docs using __module__.
* Converted DirectedGraph nodes to a list.
* Added Code of Conduct.
* Added GraphTransliterator class.
* Updated module dependencies.
* Added requirements.txt
* Added check_settings parameter to skip validating settings.
* Added tests for ambiguity and `check_ambiguity` parameter.
* Changed name to Graph Transliterator in docs.
* Created core.py, validate.py, process.py,  rules.py, initialize.py,
  exceptions.py, graphs.py
* Added ignore_errors property and setter for transliteration
  exceptions (UnrecognizableInputToken, NoMatchingTransliterationRule)
* Added logging to graphtransliterator
* Added positive cost function based on number of matched tokens in rule
* added metadata field
* added documentation

0.1.1 (2019-05-30)
------------------
* Adjusted copyright in docs.
* Removed  Python 2 support.

0.1.0 (2019-05-30)
------------------
* First release on PyPI.
