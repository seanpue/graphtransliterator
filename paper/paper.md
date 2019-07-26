---
title: "Graph Transliterator: A graph-based transliteration tool"
tags:
  - Python
  - transliteration
  - language
  - graph
authors:
  - name: A. Sean Pue
    orcid: 0000-0001-8463-8578
    affiliation: 1
affiliations:
 - name: Linguistics and Germanic, Slavic, Asian, and African Languages, Michigan State University
   index: 1
date: 23 July 2019
bibliography: paper.bib
---

# Summary

Transliteration—the representation of one language or script in the characters
or symbols of another—is a ubiquitous and important operation, used across the
humanities, social sciences, and information sciences.  It allows text to be
read by those who do not know the original alphabet. It enables the
standardized organization and search of resources, as in library systems.  It
also permits the encoding of additional information, which enables
disambiguation and advanced linguistic analysis, including natural language
processing tasks, that are often not possible in the original script.

``Graph Transliterator`` is a Python package that makes that process more
accessible by using a standardized method for encoding rules for
transliteration. It lets those rules be entered in an "easy reading" YAML
format [@YAMLAintMarkup] or directly, using standard Python data types. It
differs  from other software [@GeneralTransformsICUa] designed for handling
transliteration in two primary ways. First, other software works directly on an
input string, performing operations based on matches of particular characters.
``Graph Transliterator`` instead tokenizes the input into user-defined
transliteration token types. Then it applies transliteration rules defined for
those token types, rather than matching and manipulating the original
characters of the input string. Second, other software requires a defined
sequence of transliteration operations. ``Graph Transliterator`` instead
automatically orders its transliteration rules so that the rule involving the
largest number of tokens is applied first.

Each instance of ``Graph Transliterator`` is parameterized by the acceptable
token types of the input string as well as by transliteration rules. The
transliteration token types can be one or more letters in length, e.g. `a`,
`b`, or `aa`. Each of the token types can be assigned to particular classes,
e.g. `vowel` or `consonant`. The transliteration rules allow matching of a
particular sequence of one or more tokens. They also allow lookahead and
lookbehind matching for particular tokens or token classes.

``Graph Transliterator`` includes features that accommodate common tasks
involved in transliteration and associated forms of analysis. It includes
customizable rules for defining and handling whitespace, which is often very
important in transliteration, as many letters in non-Roman alphabets change
their shape at the start of words. It accepts "on match" rules for the
insertion of output based on which token classes are matched, e.g. the
insertion of a character between two consonants.  ``Graph Transliterator``
makes it possible for users to view the details about rule-matching, which may
enable certain forms of analysis.  It also allows the matching of all possible
rules at a given index, which can be useful in particular analysis contexts.
Each instance of a defined transliterator can be serialized and includes
metadata fields. Finally, the software includes full ambiguity checking and
produces a warning if more than one rule could match the same input. As such,
``Graph Transliterator`` provides a rigorous and reproducible framework for
transliteration.

# How It Works

![An example graph created for the simple case of a ``Graph Transliterator``
that takes two token types as input: `a` and `" "` (space), and renders `" "`
as `" "`, and `a` as `b` unless it follows a token of class `wb` (for
wordbreak), in which case it renders `a` as `B`. The `rule` nodes are in double
circles, and `token` nodes  are single circles. The numbers are the cost of
the particular edge, and less costly edges are searched first. Previous token
class (`prev_classes`) constraints are found on the edge before the leaf rule
node.\label{figure1}](figure1.png)

During initialization, a graph is created that is searched to find the best
transliteration match at a particular index in the tokens of an input string.
The graph, a directed tree, has nodes of three types: `Start`,
`token`, and `rule`.  The `Start` node is the root. A `token` node corresponds
to a token being matched. The `rule` nodes are leaves representing
transliteration rules. Each transliteration rule is assigned a particular cost
between one and zero that lessens with more tokens, using the following cost
function:

$$\text{cost}(rule) = \log_2{\big(1+\frac{1}{1+\text{count\_of\_tokens\_in}(rule)}\big)}$$

Each edge is assigned a cost corresponding to the least costly transliteration
rule leaf node that can be reached from it. Edges contain constraints that must
be met before a node can be visited. Before token nodes, these constraints
include a token in the input to be matched. Other constraints include
previous and/or following tokens or token classes. To optimize the search,
during initialization an `ordered_children` dictionary is added to each
non-leaf node. Its values  are a list of node indexes sorted by cost and keyed
by the token that follows. Any rule immediately following a node is added to
``ordered_children`` as well as to  each individual entry in it. Because of
this preprocessing, ``Graph Transliterator`` does not need to iterate through
all of the outgoing edges of a node to find the next node to search. Instead,
it uses a best-first search implemented using a stack, and will backtrack if
necessary to find the best match.

# Acknowledgements

Software development was supported by an Andrew W. Mellon Foundation New
Directions Fellowship (Grant Number 11600613) and by matching funds provided by
the College of Arts and Letters, Michigan State University.

# References
