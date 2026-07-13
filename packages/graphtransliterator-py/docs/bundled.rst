.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

=======================
Bundled Transliterators
=======================

.. note::

  Python code on this page: :jupyter-download-script:`bundled` Jupyter Notebook: :jupyter-download-notebook:`bundled`

Graph Transliterator includes bundled transliterators in a :class:`Bundled` subclass of
:class:`GraphTransliterator` that can be used as follows:

.. jupyter-execute::

  import graphtransliterator.transliterators as transliterators
  example_transliterator = transliterators.Example()
  example_transliterator.transliterate('a')

To access transliterator classes, use the iterator
:func:`transliterators.iter_transliterators`:

.. jupyter-execute::

  bundled_iterator = transliterators.iter_transliterators()
  next(bundled_iterator)

To access the names of transliterator classes, use the iterator
:func:`transliterators.iter_names`:

.. jupyter-execute::

  bundled_names_iterator = transliterators.iter_names()
  next(bundled_names_iterator)

The actual bundled transliterators are submodules of
:class:`graphtransliterator.transliterators`, but they are loaded into the namespace
of :class:`transliterators`:

.. jupyter-execute::

  from graphtransliterator.transliterators import Example

Each instance of :class:`Bundled` contains a :py:attr:`directory` attribute:

.. jupyter-execute::

  transliterator = Example()
  transliterator.directory

Each will contain an easy-reading YAML file that you can view:

.. literalinclude:: ../graphtransliterator/transliterators/example/example.yaml
  :language: yaml

There is also a JSON dump of the transliterator for quick loading:

.. literalinclude:: ../graphtransliterator/transliterators/example/example.json
  :language: json

..
.. .. jupyter-execute::
..   :hide-code:
..
..   import os
..   with open(os.path.join(transliterator.directory, "example.yaml"), "r") as f:
..     print("--Easy-reading YAML (for clarity, development, and debugging)--")
..     print(f.read()+"\n")
..   with open(os.path.join(transliterator.directory, "example.json"), "r") as f:
..     print("--JSON (for speed)--")
..     print(f.read())

Test Coverage of Bundled Transliterators
----------------------------------------

Each bundled transliterators requires rigorous testing: every node and edge, as
well as any onmatch rules, if applicable, must be visited. A separate subclass
:class:`CoverageTransliterator`  of :class:`GraphTransliterator` is used
during testing.

It logs visits to nodes, edges, and onmatch rules. The tests are found in a subdirectory
of the transliterator named "tests". They are in a YAML file consisting of a
dictionary keyed from transliteration input to correct output, e.g.:

.. literalinclude:: ../graphtransliterator/transliterators/example/tests/example_tests.yaml
  :language: yaml

Once the tests are completed, Graph Transliterator checks that all components of the
graph and all of the onmatch rules have been visited.

Class Structure and Naming Conventions
--------------------------------------
Each transliterator must include a class definition in a submodule of
:class:`transliterators`.

The class name of each transliterator must be unique and follow camel-case conventions,
e.g. `SourceToTarget`. File and directory names should, if applicable, be lowercased as
`source_to_target`.

The bundled files should follow this directory structure, where {{source_to_target}} is
the name of the transliterator:


.. code::

  transliterators
  ├── {{source_to_target}}
  |   ├── __init__.py
  |   ├── {{source_to_target}}.json
  |   ├── {{source_to_target}}.yaml
  └── tests
      ├── test_{{source_to_target}}.py
      └── {{source_to_target}}_tests.yaml

The bundled transliterator will:

- include both an easy-reading YAML file ``{{source_to_target}}.yaml`` and a
  JSON file ``{{source_to_target}}.json``.
- have tests in a YAML format consisting of a dictionary keyed from transliteration to
  correct output in ``{{source_to_target}}_tests.yaml``. It must include complete test
  coverage of its graph. Every node and edge of the graph must be visited during the
  course of the tests, as well as every on-match rule. Each on-match rule must be
  utilized during the course of the tests.
- include metadata about the transliterator in its easy-reading YAML file.
- have an optional custom test file ``test_{{source_to_target.py}}``. This is useful
  during development.

Metadata Requirements
---------------------
Each :class:`Bundled` transliterator can include the following metadata fields. These
fields are a subset of the metadata of :mod:`setuptools`.

name (`str`)
  Name of the transliterator, e.g. "source_to_target".
version	(`str`, optional)
  Version of the transliterator. Semantic versioning (https://semver.org) is
  recommended.
url	(`str`, optional)
  URL for the transliterator, e.g. github repository.
author (`str`, optional)
  Author of the transliterator
author_email (`str`, optional)
  E-mail address of the author.
maintainer (`str`, optional)
  Name of the maintainer.
maintainer_email (`str`, optional)
  E-mail address of the maintainer.
license (`str`, optional)
  License of the transliterator. An open-source license is required for inclusion in
  this project.
keywords (`list` of `str`, optional)
  List of keywords.
project_urls (`dict` of {`str`: `str`}, optional)
  Dictionary of project URLS, e.g. `Documentation`, `Source`, etc.

Metadata is validated using a :class:`BundledMetadataSchema` found in
:mod:`transliterators.schemas`.

To browse metadata, you can use :func:`iter_transliterators`:


.. jupyter-execute::

  import pprint
  transliterator = next(transliterators.iter_transliterators())
  pprint.pprint(transliterator.metadata)
