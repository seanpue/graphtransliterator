=======
History
=======

[Unreleased - Maybe]
--------------------
* Add CLI.
* Add metadata guidelines
* Save match location in tokenize
* Reconsider serialization keys
* Add tests directly to YAML files
* Allow insertion of transliteration error messages into output.

[Unreleased-TODO]
-----------------

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
