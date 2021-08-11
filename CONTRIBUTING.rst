.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

Contributor Code of Conduct
---------------------------
Please note that this project is released with a :doc:`Contributor Code of
Conduct <code_of_conduct>`. By participating in this project you agree to
abide by its terms.

Types of Contributions
----------------------

You can contribute in many ways:

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/seanpue/graphtransliterator/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Graph-based Transliterator could always use more documentation, whether as part of the
official Graph-based Transliterator docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/seanpue/graphtransliterator/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Add Transliterators
~~~~~~~~~~~~~~~~~~~

We welcome new transliterators to be added to the bundled transliterators!

See the documentation about Bundled Transliterators and look at Example as a model.

Raise an issue on Github, https://github.com/seanpue/graphtransliterator/issues

Then create a new branch with the new transliterator. Make sure the transliterator
passes all of these requirements:

  - is a submodule of graphtransliterator.transliterators
  - has a unique name, preferably in format source_to_target
  - has the following files:
    - __init__.py
    - {{source_to_target}}.yaml
    - {{source_to_target}}.json
    - tests/{{source_to_target}}_tests.yaml
    - tests/test_{{source_to_target}}.py (optional)
  - has a classname in camel case, e.g. SourceToTarget
  - has complete test coverage of all nodes and edges of generated graph and all onmatch
    rules, if present
  - has required metadata in the YAML file.

When all the requirements are fulfilled, submit a pull request, and it will be reviewed
for inclusion in a near-future release.


Get Started!
------------

Ready to contribute? Here's how to set up `graphtransliterator` for local
development.

1. Fork the `graphtransliterator` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/graphtransliterator.git

3. Install your local copy into a virtualenv. Assuming you have
   virtualenvwrapper installed, this is how you set up your fork for local
   development::

    $ mkvirtualenv graphtransliterator
    $ cd graphtransliterator/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, format your code using the Black code
   formatter. (You can do that in your editor, as well). Then check that your
   changes pass flake8 and the tests, including testing other Python versions
   with tox::

    $ black graphtransliterator
    $ flake8 graphtransliterator tests
    $ python setup.py test or py.test
    $ tox

   To get black, flake8, and tox, just pip install them into your virtualenv.

   You should also test your coverage using make:

    $ make coverage

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.7 and 3.8 for PyPy. Check
   https://travis-ci.org/seanpue/graphtransliterator/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ py.test tests.test_graphtransliterator


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bumpversion patch # possible: major / minor / patch
$ git push
$ git push --tags

The module uses Github Actions to deploy to TestPyPI and to PyPI.
