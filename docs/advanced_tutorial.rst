.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

.. _`Advanced Tutorial`:

============================================
Advanced Tutorial: Bundling a Transliterator
============================================

This advanced tutorial builds upon the original tutorial to show you how to bundle a
transliterator for inclusion in Graph Transliterator.

Contributions to Graph Transliterator are strongly encouraged!

You will make a very simple transliterator while going through the steps of bundling it
into Graph Transliterator.

Git Basics: Fork, Branch, Sync, Commit
======================================

Fork
----

The first thing to do, if you have not already, is to create a fork of Graph
Transliterator.  See https://help.github.com/en/articles/fork-a-repo

(From here on out, we will be using the command line.)

After creating a fork, clone your forked repo:

.. code-block:: bash

  git clone https://github.com/YOUR-USERNAME/graphtransliterator

Branch
------

Once you have done that, go into that directory and create a new branch:

.. code-block:: bash

  cd graphtransliterator
  git checkout -b [name_of_your_transliterator_branch]

For this example, you can use the branch `a_to_b`:

.. code-block:: bash

  cd graphtransliterator
  git checkout -b a_to_b

Then, push that branch to the origin (your personal github fork):

.. code-block:: bash

  git push origin [name_of_your_transliterator_branch]

  Here that would be:

  .. code-block:: bash

    git push origin a_to_b


Next, add a remote upstream for Graph Transliterator (the official Graph Transliterator
repo):

.. code-block:: bash

    git remote add upstream https://github.com/seanpue/graphtransliterator.git

Sync
----

To update your local copy of the the remote (official Graph Transliterator repo), run:

.. code-block:: bash

    git fetch upstream

To sync your personal fork with the remote, run:

.. code-block:: bash

    git merge upstream/master

See https://help.github.com/en/articles/syncing-a-fork for more info.
You can run the previous two commands at any time.

Commit
------

You can commit your changes by running:

.. code-block:: bash

    git commit -m 'comment here about the commit'

Adding A Transliterator
=======================

To add a transliterator, the next step is to create a subdirectory in
``transliterators``.  For this tutorial, you can make a branch named ``a_to_b``.

Note that this will be under ``graphtransliterator/transliterators``, so from the
root directory enter:

.. code-block:: bash

    cd graphtransliterator/transliterators
    mkdir [name_of_your_transliterator]
    cd [name_of_your_transliterator]

For this example, you would enter:


.. code-block:: bash


    cd graphtransliterator/transliterators
    mkdir a_to_b
    cd a_to_b


In the ``graphtransliterator/transliterators/[name_of_your_transliterator]`` directory,
you will add:

  - an `__init__.py`
  - a YAML file in the "easy reading format"
  - a JSON file that is a serialization of the transliterator (optional)
  - a ``tests`` directory including a file named ``[name_of_your_transliterator]_tests.yaml``
  - a Python test named ``test_[name_of_your_transliterator].py`` (optional)

Here is a tree showing the file organization:

.. code::

  transliterators
  ├── {{source_to_target}}
  |   ├── __init__.py
  |   ├── {{source_to_target}}.json
  |   ├── {{source_to_target}}.yaml
  └── tests
      ├── test_{{source_to_target}}.py
      └── {{source_to_target}}_tests.yaml

YAML File
---------

The YAML file should contain the "easy reading" version of your transliterator.
For this example, create a file called ``a_to_b.yaml``.  Add a ``metadata`` field to the
YAML file, as well, following the guidelines.

.. code-block:: yaml

  tokens:
    a: [a_class]
    ' ': [whitespace]
  rules:
    a: A
  onmatch_rules:
    - <a_class> + <a_class>: ","
  whitespace:
    default: ' '
    token_class: whitespace
    consolidate: false
  metadata:
    name: A to B
    version: 0.0.1
    url: http://website_of_project.com
    author: Your Name is Optional
    author_email: your_email@is_option.al
    maintainer: Maintainer's Name is Optional
    maintainer_email: maintainers_email@is_option.al
    license: MIT or Other Open Source License
    keywords: [add, keywords, here, as, a, list]
    project_urls:
       Documentation: https://link_to_documentation.html
       Source: https://link_to_sourcecode.html
       Tracker: https://link_to_issue_tracker.html

For most use cases, the ``project_urls`` can link to the Graph Transliterator
Github page.

JSON File
---------

To create a JSON file, you can use the command line interface:

  $ graphtransliterator dump --from yaml_file a_to_b.yaml > a_to_b.json

Alternatively, you can use the ``make-json`` command:

  $ graphtransliterator make-json AToB

The JSON file loads more quickly than the YAML one, but it is not necessary during
development.

__init__.py
-----------

The `__init__.py` will create the bundled transliterator, which is a subclass of
`GraphTransliterator` named `Bundled`.

Following convention, uou need to name your transliterator's class is CamelCase. For
this example, it would be ``AToB``:

.. code::

  from graphtransliterator.transliterators import Bundled

  class AToB(Bundled):
      """
      A to B Bundled Graph Transliterator
      """

      def __init__(self, **kwargs):
          """Initialize transliterator from YAML."""
          self.from_YAML(
              **kwargs
          )  # defaults to check_ambiguity=True, check_coverage=True
          # When ready, remove the previous lines and initialize more quickly from JSON:
          # self.init_from_JSON(**kwargs) # check_ambiguity=False, check_coverage=False


When you load the bundled transliterator from YAML using ``from_YAML`` it will check
for ambiguity as well as check the coverage of the tests. You can turn those features
off temporarily here.

When a transliterator is added into Graph Transliterator, it will likely be set to load
from JSON by default. Tests will check for ambiguity and coverage.


Tests
-----
Graph Transliterator requires that all bundled transliterators have tests that visit
every edge and node of the internal graph and that use all on-match rules. The test file
should be a YAML file defining a dictionary keyed from input to correct output.

You can test the transliterator as you are developing it by adding YAML tests and
running the command:


.. code-block:: bash

    graphtransliterator test [name_of_your_transliterator]

Tests can be generated using the command line interface:

.. code-block:: bash

    mkdir tests
    graphtransliterator generate-tests --from bundled [name_of_your_transliterator] > tests/[name_of_your_transliterator]

Testing the Transliterator
==========================
You should test the transliterator to make sure everything is correct, including its
metadata. To do that, navigate back to the root directory of `graphtransliterator`
and execute the command:

.. code-block:: bash

  py.test tests/test_transliterators.py

You can also run the complete suite of tests by running:

.. code-block:: bash

  tox

Pushing Your Transliterator
===========================
When you are finished with a version of your transliterator, you should once again
commit it to your github branch after syncing your branch with the remote. Then you can
make a pull request to include the transliterator in Graph Transliterator. You can do
that from the Graph Transliterator Github page.
See https://help.github.com/en/articles/creating-a-pull-request-from-a-fork.
