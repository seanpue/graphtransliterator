.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

API Reference
=============


A list of the full API reference of all public classes and functions
is below.

Public members can (and should) be imported from :class:`graphtransliterator`::

  from graphtransliterator import GraphTransliterator

Bundled transliterators require that :class:`graphtransliterator.transliterators`:
be imported:

  import graphtransliterator.transliterators
  transliterators.iter_names()

.. module:: graphtransliterator

Core Classes
------------

.. autoclass:: GraphTransliterator
   :members:

.. autoclass:: CoverageTransliterator
   :members:

Graph Classes
-------------

.. autoclass:: DirectedGraph
   :members:

.. autoclass:: VisitLoggingDirectedGraph
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
