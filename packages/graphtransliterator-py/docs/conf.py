#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Optional fallback, though Poetry handles this environment-wide
sys.path.insert(0, os.path.abspath(".."))

import graphtransliterator  # noqa

# -- General configuration ---------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.imgconverter",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_issues",
    "jupyter_sphinx",
]

# Github repo settings
issues_github_path = "seanpue/graphtransliterator"
issues_uri = "https://github.com/seanpue/graphtransliterator/issues/{issue}"
issues_pr_uri = "https://github.com/seanpue/graphtransliterator/pull/{pr}"
issues_commit_uri = "https://github.com/seanpue/graphtransliterator/commit/{commit}"

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
templates_path = ["_templates"]
source_suffix = ".rst"

# Modernized root document config
root_doc = "index"

# General information about the project.
project = "Graph Transliterator"
copyright = "2020, Michigan State University"
author = "A. Sean Pue"

# Dynamic versions pulled safely from package initialization
version = graphtransliterator.__version__
release = graphtransliterator.__version__

# Corrected for Sphinx 9.x compliance
language = "en"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "default"
todo_include_todos = False

# -- Options for HTML output -------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
htmlhelp_basename = "graphtransliteratordoc"

# -- Options for LaTeX output ------------------------------------------

latex_engine = "xelatex"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

latex_documents = [
    (
        root_doc,
        "graphtransliterator.tex",
        "Graph Transliterator Documentation",
        "A. Sean Pue",
        "manual",
    )
]

# -- Options for manual page output ------------------------------------

man_pages = [
    (
        root_doc,
        "graphtransliterator",
        "Graph-based Transliterator Documentation",
        [author],
        1,
    )
]

# -- Options for Texinfo output ----------------------------------------

texinfo_documents = [
    (
        root_doc,
        "graphtransliterator",
        "Graph Transliterator Documentation",
        author,
        "graphtransliterator",
        "A graph-based transliteration tool.",
        "Miscellaneous",
    )
]

# jupyter-sphinx configuration
jupyter_sphinx_linenos = True
jupyter_sphinx_continue_linenos = True