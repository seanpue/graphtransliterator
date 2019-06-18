=======
History
=======

[Unreleased - Maybe]
====================
* Add CLI.
* add _to_metadata function
* Save match location in tokenize
* reconsider serialization keys
* add tests directly to YAML files
* make pruned_of more elegant
* Allow insertion of transliteration error messages into output.

[Unreleased-TODO]
=================
* Add metadata guidelines and validation.
* Document error handling and logging.
* Add and check examples in docstring.
* Add notes about YAML handling of unicode charnames, link to YAML.
* Add usage example

0.1.2 (####-##-##)
==================
* Fixed  module naming in docs using __module__.
* Converted DirectedGraph nodes to a list.
* Add Code of Conduct.
* Added GraphTransliterator class.
* Updated module dependencies.
* Added check_settings parameter to skip validating settings.
* Added tests for ambiguity and `check_ambiguity` parameter.
* Changed name to Graph Transliterator in docs.
* Created validate.py, process.py,  rules.py, initialize.py, exceptions.py,
  graph.py
* Added ignore_errors property and setter for transliteration
  exceptions (UnrecognizableInputToken, NoMatchingTransliterationRule)
* Added logging to graphtransliterator
* Added positive cost function based on number of matched tokens in rule
* added metadata field

0.1.1 (2019-05-30)
==================
* Adjust copyright in docs.
* Removed  Python 2 support.

0.1.0 (2019-05-30)
------------------
* First release on PyPI.
