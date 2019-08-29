API Reference
=============


A list of the full API reference of all public classes and functions
is below.

Public members can (and should) be imported from :class:`graphtransliterator`::

  from graphtransliterator import GraphTransliterator

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

Exceptions
----------

.. autoexception:: GraphTransliteratorException

.. autoexception:: AmbiguousTransliterationRulesException

.. autoexception:: NoMatchingTransliterationRuleException

.. autoexception:: UnrecognizableInputTokenException

Schemas
-------

.. autoclass:: DirectedGraphSchema

.. autoclass:: EasyReadingSettingsSchema

.. autoclass:: GraphTransliteratorSchema

.. autoclass:: OnMatchRuleSchema

.. autoclass:: SettingsSchema

.. autoclass:: TransliterationRuleSchema

.. autoclass:: WhitespaceDictSettingsSchema

.. autoclass:: WhitespaceSettingsSchema
