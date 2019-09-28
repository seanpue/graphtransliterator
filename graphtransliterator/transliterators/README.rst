==============================
Bundled Transliterators--DRAFT
==============================
This directory contains bundled transliterators. Each transliterator is in a directory
off of `transliterators.` The root directory contains the transliterators as YAML files.
The subdirectory `tests` contains tests for each transliterator.

If you are creating a transliterator, see the `example` subdirectory. To be included,
the transliterator's tests must have complete coverage of its graph, as well as its
onmatch rules, if applicable. Every node and edge of the graph must be visited during
the course of the tests, as well as every onmatch rule.

Naming Conventions
------------------
The class name of each transliterator must be unique and follow camel-case-conventions,
e.g. `SourceToTarget`. File and directory names should, if applicable, be lowercased as
`source_to_target`.

The bundled files should follow this directory structure:

transliterators
    source_to_target
        __init__.py
        source_to_target.json
        source_to_target.yaml
    tests
        test_source_to_target.py
        test_source_to_target.yaml

Metadata Requirements
---------------------
Each transliterator can include the following metadata fields. These fields are a
subset of `setuptools`. Long descriptions are not currently included.

name (`str`)
  Name of the transliterator, e.g. "source_to_target". Associated JSON (faster!) and
  easy reading YAML files (slower but should be included) should be named accordingly.

  If possible, the `name` should be in lowercase and follow the format:
  `source_to_target.yaml`, where `source` is the original script/language/etc. and
  `target` is the destination script/language/etc.
version	(`str`, optional)
  Version of the transliterator. Semantic versioning (https://semver.org) is
  strongly recommended.
url	(`str`, optional)
  URL for the transliterator, e.g. githubrepository repository.
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
  List of keywords
project_urls (`dict` of {`str`: `str`}, optional)
  Dictionary of project URLS, e.g. `Documentation`, `Source`, etc.
