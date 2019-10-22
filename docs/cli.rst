
======================
Command Line Interface
======================
Graph Transliterator has a simple command line interface with four commands:
``dump``, ``generate-tests``, ``test``, and ``transliterate``.


.. jupyter-kernel:: bash
    :id: cli_kernel

.. jupyter-execute::

  graphtransliterator --help


Dump
----

The ``dump`` command will output the specified transliterator as JSON:

.. jupyter-execute::

  graphtransliterator dump --help

It require a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled` or `yaml_file`) and the
second a parameter for that format (the name of the bundled transliterator or the name
of a YAML file).

To load a bundled transliterator, give its name, which will be in camel case:

.. jupyter-execute::

  graphtransliterator dump --from bundled Example

To load from a yaml file, give the name of the file:


.. jupyter-execute::

  graphtransliterator dump --from yaml_file ../graphtransliterator/transliterators/example/example.yaml

If you want to check for ambiguity in the transliterator before the dump, use the
--`check-ambiguity` or `-ca` option:


.. jupyter-execute::

  graphtransliterator dump --from bundled Example --check-ambiguity


Generate Tests
--------------

The ``generate-tests`` command generates YAML tests keyed from input to desired output
covering the entire internal graph. This command can be used to view the output of the
transliterator in Unicode. It can also be used to generate starter tests for bundled
transliterators:

.. jupyter-execute::

  graphtransliterator generate-tests --help


It also require a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled`, `json`, `json_file`, `yaml_file`),
and the second a parameter for that format (the name of the bundled transliterator, the
actual JSON, or the name of a YAML file). Ambiguity checking can be turned on using
``--check_ambiguity`` or ``-ca``:

.. jupyter-execute::

  graphtransliterator generate-tests --from bundled Example


Test
----
The `test` command tests a bundled transliterator:


.. jupyter-execute::

  graphtransliterator test --help

It can only be used with bundled transliterators, and so it  only needs the name of the
transliterator as its argument. This feature is useful when developing a transliterator.
You can write the tests first and then begin developing the transliterator:

.. jupyter-execute::

  graphtransliterator test Example


Transliterate
-------------
The `transliterate` command will transliterate any following arguments:


.. jupyter-execute::

  graphtransliterator transliterate --help


It also require a ``--from`` or ``-f`` option with two arguments. The first argument
specifies the format of the transliterator (`bundled`, `json`, `json_file`, `yaml_file`),
and the second a parameter for that format (the name of the bundled transliterator, the
actual JSON, or the name of a YAML file).

The `transliterate` command will transliterate every argument that follows. If there is
only one input string, it will return a string:


.. jupyter-execute::

  graphtransliterator transliterate --from bundled Example a

.. jupyter-execute::

  graphtransliterator transliterate -f json_file ../graphtransliterator/transliterators/example/example.json a

.. jupyter-execute::

  graphtransliterator transliterate -f yaml_file ../graphtransliterator/transliterators/example/example.yaml a

Otherwise, it will return a list:

.. jupyter-execute::

  graphtransliterator transliterate -f bundled Example a a

The `transliterate` command also an optional ``--to`` or ``-t`` command that specifies
the output format, a `python` string (default) or a `json` string:

.. jupyter-execute::

  graphtransliterator transliterate --from bundled Example --to python a

.. jupyter-execute::

  graphtransliterator transliterate --from bundled Example --to json a

.. jupyter-execute::

  graphtransliterator transliterate --from bundled Example --to python a a

.. jupyter-execute::

  graphtransliterator transliterate --from bundled Example --to json a a
