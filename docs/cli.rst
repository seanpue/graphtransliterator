
.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

.. jupyter-execute::
  :hide-code:

  import graphtransliterator
  import graphtransliterator.cli as cli
  from click.testing import CliRunner
  runner = CliRunner()
  def run(func, parameters):
    print(runner.invoke(func, parameters).output)

======================
Command Line Interface
======================
Graph Transliterator has a simple command line interface with six commands:
``dump``, ``dump-tests``, ``generate-tests``, ``list-bundled``, ``make-json``, ``test``,
and ``transliterate``.


.. code-block:: console

  $ graphtransliterator --help

.. jupyter-execute::
  :hide-code:

  run(cli.main, ['--help'])

Dump
----

The ``dump`` command will output the specified transliterator as JSON:

.. code-block:: console

  $ graphtransliterator dump --help

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--help'])


It require a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled` or `yaml_file`) and the
second a parameter for that format (the name of the bundled transliterator or the name
of a YAML file).

To load a bundled transliterator, used `bundled` as the first parameter and give its
(class) name, which will be in CamelCase, as the second:

.. code-block:: console

  $ graphtransliterator dump --from bundled Example

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'bundled', 'Example'])



To load from a YAML file, give `yaml_file` as the first and the the name of the file as
the second parameter:

.. code-block:: console

  $ graphtransliterator dump --from yaml_file ../graphtransliterator/transliterators/example/example.yaml


.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'yaml_file', '../graphtransliterator/transliterators/example/example.yaml'])

If you want to check for ambiguity in the transliterator before the dump, use the
``--check-ambiguity`` or ``-ca`` option:

.. code-block:: console

  $ graphtransliterator dump --from bundled Example --check-ambiguity # human readable

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'bundled', 'Example', '--check-ambiguity']) # not human readable, with graph

The compression level can of the JSON be specified using the ``--compression-level`` or
``-cl`` command. Compression level 0 is human readable; compression level 1 is not human
readable and includes the generated graph; compression level 2 is not human readable
and does not include the graph. Compression level 2, which is the fastest, is the
default. There is no information lost during these compressions:

.. code-block:: console

  $ graphtransliterator dump --from bundled Example --compression-level 0 # human readable, with graph

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '0'])

.. code-block:: console

  $ graphtransliterator dump --from bundled Example --compression-level 1 # not human readable, with graph

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '1'])

.. code-block:: console

  $ graphtransliterator dump --from bundled Example --compression-level 2 # default; not human readable, no graph

.. jupyter-execute::
  :hide-code:

  run(cli.dump, ['--from', 'bundled', 'Example', '--compression-level', '2'])

Dump Tests
----------

The ``dump-tests`` command dumps the tests of a bundled transliterator:


.. code-block:: console

  $ graphtransliterator dump-tests --help

.. jupyter-execute::
  :hide-code:

  run(cli.dump_tests, ['--help'])

By default, it outputs the original YAML tests file, preserving any comments:

.. code-block:: console

  $ graphtransliterator dump-tests Example

.. jupyter-execute::
  :hide-code:

  run(cli.dump_tests, ['Example'])

To output as JSON, use the ``--to`` or ``-t`` flag:

.. code-block:: console

  $ graphtransliterator dump-tests --to json Example

.. jupyter-execute::
  :hide-code:

  run(cli.dump_tests, ['--to', 'json', 'Example'])

Generate Tests
--------------

The ``generate-tests`` command generates YAML tests keyed from input to desired output
covering the entire internal graph. This command can be used to view the output of the
transliterator in Unicode. It can also be used to generate starter tests for bundled
transliterators:

.. code-block:: console

  $ graphtransliterator generate-tests --help

.. jupyter-execute::
  :hide-code:

  run(cli.generate_tests, ['--help'])

It also require a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled`, `json`, `json_file`, `yaml_file`),
and the second a parameter for that format (the name of the bundled transliterator, the
actual JSON, or the name of a YAML file). Ambiguity checking can be turned on using
``--check_ambiguity`` or ``-ca``:

.. code-block:: console

  $ graphtransliterator generate-tests --from bundled Example

.. jupyter-execute::
  :hide-code:

  run(cli.generate_tests, ['--from', 'bundled', 'Example'])


List Bundled Transliterators
----------------------------
The ``list-bundled`` command provides a list of bundled transliterators:

.. code-block:: console

  $ graphtransliterator test --help


Make JSON of Bundled Transliterator(s)
--------------------------------------
The ``make-json`` command makes new JSON files of bundled transliterators:

.. code-block:: console

  $ graphtransliterator make-json --help

It also allows regular-expression matching using the ``--reg-ex`` or ``-re`` flag.
Matching starts at the start of the string. This command is for people creating
new bundled transliterators.

Test
----
The ``test`` command tests a bundled transliterator:

.. code-block:: console

  $ graphtransliterator test --help

.. jupyter-execute::
  :hide-code:

  run(cli.test, ['--help'])

It can only be used with bundled transliterators, so it only needs the name of the
transliterator as its argument. This feature is useful when developing a transliterator.
You can write the tests first and then begin developing the transliterator:

.. code-block:: console

  $ graphtransliterator test Example

.. jupyter-execute::
  :hide-code:

  run(cli.test, ['Example'])

Transliterate
-------------
The ``transliterate`` command will transliterate any following arguments:

.. code-block:: console

  $ graphtransliterator transliterate --help

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['--help'])

It also requires a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled`, `json`, `json_file`,
`yaml_file`), and the second a parameter for that format (the name of the bundled
transliterator, the actual JSON, or the name of a YAML file).

The `transliterate` command will transliterate every argument that follows. If there is
only one input string, it will return a string:

.. code-block:: console

  $ graphtransliterator transliterate --from bundled Example a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['--from', 'bundled', 'Example', 'a'])

.. code-block:: console

  $ graphtransliterator transliterate -f json_file ../graphtransliterator/transliterators/example/example.json a


.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'json_file', '../graphtransliterator/transliterators/example/example.json', 'a'])

.. code-block:: console

  $ graphtransliterator transliterate -f yaml_file ../graphtransliterator/transliterators/example/example.yaml a


.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'yaml_file', '../graphtransliterator/transliterators/example/example.yaml', 'a'])

Otherwise, it will return a list:

.. code-block:: console

  $ graphtransliterator transliterate -f bundled Example a a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'json_file', '../graphtransliterator/transliterators/example/example.json', 'a', 'a'])


The `transliterate` command also an optional ``--to`` or ``-t`` command that specifies
the output format, a ```python`` string (default) or a ``json`` string:

.. code-block:: console

  $ graphtransliterator transliterate --from bundled Example a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'bundled', 'Example', 'a'])

.. code-block:: console

  $ graphtransliterator transliterate --from bundled Example --to json a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'json', 'a'])

.. code-block:: console

  $ graphtransliterator transliterate --from bundled Example --to python a a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'python', 'a', 'a'])

.. code-block:: console

  $ graphtransliterator transliterate --from bundled Example --to json a a

.. jupyter-execute::
  :hide-code:

  run(cli.transliterate, ['-f', 'bundled', 'Example', '--to', 'json', 'a', 'a'])
