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
be imported::

  import graphtransliterator.transliterators
  transliterators.iter_names()

.. module:: graphtransliterator

Core Classes
------------

.. autoclass:: GraphTransliterator
   :members:

.. autoclass:: CoverageTransliterator
   :members:

Bundled Transliterators
-----------------------

.. automodule:: graphtransliterator.transliterators
  :members:

Graph Classes
-------------

.. autoclass:: graphtransliterator.DirectedGraph
   :members:

.. autoclass:: graphtransliterator.VisitLoggingDirectedGraph
   :members:

Rule Classes
------------

.. autoclass:: graphtransliterator.TransliterationRule

.. autoclass:: graphtransliterator.OnMatchRule

.. autoclass:: graphtransliterator.WhitespaceRules

Exceptions
----------

.. autoexception:: graphtransliterator.GraphTransliteratorException

.. autoexception:: graphtransliterator.AmbiguousTransliterationRulesException

.. autoexception:: graphtransliterator.NoMatchingTransliterationRuleException

.. autoexception:: graphtransliterator.UnrecognizableInputTokenException

Schemas
-------

.. autoclass:: graphtransliterator.DirectedGraphSchema

.. autoclass:: graphtransliterator.EasyReadingSettingsSchema

.. autoclass:: graphtransliterator.GraphTransliteratorSchema

.. autoclass:: graphtransliterator.OnMatchRuleSchema

.. autoclass:: graphtransliterator.SettingsSchema

.. autoclass:: graphtransliterator.TransliterationRuleSchema

.. autoclass:: graphtransliterator.WhitespaceDictSettingsSchema

.. autoclass:: graphtransliterator.WhitespaceSettingsSchema
