=======
History
=======

[Unreleased - Maybe]
====================
* Add CLI.
* Convert DirectedGraph nodes to a list.
* add _to_metadata function
* locate and warn about tying transliteration rules
* Add safe transliterate that does match_all and locates tying best results.
* Save match location in tokenize
* Adjust base of cost according to max number of tokens

[Unreleased-TODO]
=================
* Add metadata guidelines and validation.
* Add Code of Conduct.
* Fix module naming in docs.
* Decide error handling and logging.
* Add and check examples in docstring.

0.1.2 (####-##-##)
==================
* Added GraphTransliterator class.
* Updated module dependencies.
* Changed name to Graph Transliterator in docs.
* Created validate.py, process.py,  types.py, initialize.py, exceptions.py
* Added ignore_exceptions property (default: False) for transliteration
  exceptions (UnrecognizableInputToken, NoMatchingTransliterationRule)
  with setter
* Adding logging to 'graphtransliterator' for exceptions
* Added positive cost function based on number of matched tokens in rule

0.1.1 (2019-05-30)
==================
* Adjust copyright in docs.
* Removed  Python 2 support.

0.1.0 (2019-05-30)
------------------
* First release on PyPI.
