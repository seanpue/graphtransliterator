API Reference
=============


A list of the full API reference of all public classes and functions
is below.

Public members can (and should) be imported from :class:`graphtransliterator`::

  from graphtransliterator import GraphTransliterator, validate_raw_settings

.. module:: graphtransliterator

Core Classes
------------

.. autoclass:: GraphTransliterator
   :members:

Graph Classes
-------------

.. autoclass:: DirectedGraph
   :members:

Rule Classes
------------

.. autoclass:: TransliterationRule

.. autoclass:: OnMatchRule

.. autoclass:: WhitespaceRules

Validation Functions
--------------------

.. autofunction:: validate_easyreading_settings

.. autofunction:: validate_settings

Exceptions
----------

.. autoexception:: GraphTransliteratorException

.. autoexception:: AmbiguousTransliterationRulesException

.. autoexception:: NoMatchingTransliterationRuleException

.. autoexception:: UnrecognizableInputTokenException
