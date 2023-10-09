=======
History
=======

[Unreleased - Maybe]
--------------------
* save match location in tokenize using token_details
* allow insertion of transliteration error messages into output
* fix Devanagari output in Sphinx-generated Latex PDF
* add translated messages
* add precommit to run black
* add static typing with mypy
* adjust IncorrectVersionException to only consider major, minor versioning not patch
* Adjust CSS for CLI output in docs

[To do]
-------
* Add on/off switch characters
* fix coverage

1.2.3 (2023-10-09)
------------------
* added python 3.10, 3.11, removed <=3.8
* updated dependencies (used pur)
* updated jupyter-download syntax
* reformatted with black
* adjusted flake8 line length
* removed collect_ignore for pytest
* updated Github actions

1.2.2 (2021-08-11)
------------------

* updated CONTRIBUTING.rst for new Python versions
* added github actions to publish to pypi and testpypi
* shifted to github CI
* updated dependencies
* fixed tox.ini
* updated schema.py error message
* updated docs/conf.py for jupyter_sphinx

1.2.1 (2020-10-29)
------------------
* updated docs/conf.py for jupyter_sphinx

1.2.0 (2020-05-13)
------------------
* changes to bundled.py and cli.py with dump-tests command
* updated cli.rst

1.1.2 (2020-04-29)
------------------
* updated LICENSE, minor code updates, security updates

1.1.1 (2020-04-21)
------------------
* Added test to check compressed dump is uniform
* Fixed sorting of class id in compressed dump to make JSON output uniform
* Added Python 3.8 support

1.1.0 (2020-01-10)
------------------
* Added pre-commit hook to rebuild bundled transliterators with bump2version
* remove to_dict from DirectedGraph, since it is handled through Marshmallow schemas.
* Adjust documentation to mention compression.
* added list-bundled CLI command
* added --regex/-re flag to graphtransliterator make-json CLI command to allow regular
  expressions
* removed coverage keyword from GraphTransliterator
* reorganized core.py
* converted from_dict, from_easyreading_dict, from_yaml, and from_yaml_file to static
  methods from class methods
* moved ambiguity-checking functions to ambiguity.py and tests to test_ambiguity.py
* set three levels of compression: 0 (Human-readable), 1 (no data loss, includes graph),
  2 (no data loss, and no graph); 2 is fastest and set to default.
* set check_ambiguity to read keyword during JSON load
* allowed empty string productions during JSON compression
* added compression.py with decompress_config() and compress_config() to compress JSON
* added tests/test_compression.py to test compression.py
* added sorting of edge_list to DirectedGraph to allow dumped JSON comparison in tests
* adjusted _tokenizer_string_from() to sort by length then string for JSON comparison

1.0.7 (2019-12-22)
------------------
* added IncorrectVersionException, if serialized version being
  loaded is from a later version than the current graphtransliterator
  version
* added automatic edge_list creation if edge parameter in DirectedGraph
* added fields to and started using NodeDataSchema
* added pre_dump to GraphTransliteratorSchema, NodeDataSchema to remove empty values
  to compress Serialization
* removed rule from graph leaves and updated docs accordingly

1.0.6 (2019-12-15)
------------------
* fixed serialization of graph node indexes as integer rather than strings

1.0.5 (2019-12-14)
------------------
* added JOSS citation to README
* added --version to cli
* removed some asserts
* removed rule dictionaries from graph leaves to compress and simplify serialization

1.0.4 (2019-11-30)
------------------
* updates to docs

1.0.3 (2019-11-30)
------------------
* update to paper

1.0.2 (2019-11-30)
------------------
* updates for Zenodo

1.0.1 (2019-11-29)
------------------
* updated requirements_dev.txt

1.0.0 (2019-11-26)
------------------
* removed extraneous files
* updated development status in setup.py
* set to current jupyter-sphinx

0.4.10 (2019-11-04)
-------------------
* fixed typo in requirements_dev.txt

0.4.9 (2019-11-04)
------------------
* quick fix to requirements_dev.txt due to readthedocs problem with not reading changes

0.4.8 (2019-11-04)
------------------
* twine update to 2.0

0.4.7 (2019-11-04)
------------------
* temp switch back to dev version of jupyter-sphinx for overflow error
* Dropped Python 3.5 support for twine 2.0 update

0.4.6 (2019-11-04)
------------------
* switched to latest jupyter-sphinx
* travis adjustments

0.4.5 (2019-10-31)
------------------
* Adjusted make-json CLI test to restore original example.json

0.4.4 (2019-10-24)
------------------
* moved README.rst to include in index.rst
* fixed error in advanced_tutorial.rst

0.4.3 (2019-10-24)
------------------
* fixed requirements_dev.txt

0.4.2 (2019-10-24)
------------------
* fixed README.rst for PyPI

0.4.1 (2019-10-24)
------------------
* fixed links to code in docs
* fixed link to NOTICE
* added acknowledgements

0.4.0 (2019-10-24)
------------------
* added bundled transliterators to api.rst
* adjustments to usage.rst
* adjustments to tutorial.rst
* fixes to docs (linking module)
* adjustments to advanced_tutorial.rst
* adjustments to README.rst
* fixes to AUTHORS.rst
* added kudos.rst to docs to acknowledge inspirational projects
* added advanced tutorial on bundling a transliterator.
* added cli.rst to docs
* fixed regex in get_unicode_char to allow hyphen
* added cli.py and adjusted setup.py
* updated tutorial
* added statement of need to README. Thanks :user:`rlskoeser`.
* Removed continue-linenos jupyter-sphinx directive in favor of configuration settings
* added preface to documentation source files with links to production version, etc.
  Thanks :user:`rlskoeser`.
* added custom css for jupyter-sphinx cells
* added jupyter-sphinx documentation with line numbering
* removed pkg_resources as source for version due to problem with loading from
  pythonpath for jupyter-sphinx in readthedocs, instead used __version__
* adjust path in docs/conf.py to fix docs error
* added bundled/schemas.py with MetadataSchema for bundled transliterator metadata
* added coverage to from_dict()
* added allow_none in onmatch_rules in GraphTransliteratorSchema
* adjusted core.py so that all edges are visited during search, even if no constraints
* removed _count_of_tokens() in favor of cost
* added IncompleteGraphCoverageException to exceptions.py
* added VisitLoggingDirectedGraph to graphs.py
* added tests/test_transliterator.py
* partially updated transliterators/README.rst
* removed transliterators/sample/*
* added yaml and json to package_data in setup.py
* Added to core.py class CoverageTransliterator, which tracks visits to
  edges, nodes, and onmatch rules, and allows clearing of visits and checking of
  coverage, used to make sure tests are comprehensive
* created test/test_coverage.py to test CoverageTransliterator
* created transliterators/bundled.py with class Bundled for bundled transliterators
* added load_from_YAML() and load_from_JSON() initializers to Bundled to load from
  bundled YAML (for development) and JSON (for speed)
* added load_yaml_tests(), run_yaml_tests(), and run_tests() to Bundled
* created transliterators/__init__.py that finds bundled transliterators in subdirectory
  and adds them to  graphtransliterators.transliterators namespace
* added iter_names() and iter_transliterators() to transliterators/__init__.py
* created test/test_transliterator.py to check bundled transliterator loading and
  functions
* created in transliterators/example/ __init__.py, example.json, example.yaml
* created in transliterators/example/tests test_example.py and example_tests.yaml

0.3.8 (2019-09-18)
------------------
* fixed load() docstring example
* updated check_ambiguity() to use cost


0.3.7 (2019-09-17)
------------------
* Adjusted docs to show readme as first page
* Added sample graph and code to README.rst
* moved images in docs to _static

0.3.6 (2019-09-17)
------------------
* adjusted installation.rst renaming libraries to modules
* updated paper and bibliography.

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
