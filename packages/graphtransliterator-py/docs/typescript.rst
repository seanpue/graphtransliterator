.. _typescript:

===================
TypeScript Port
===================

A high-performance string matching and deterministic token transformation graph framework written in native TypeScript. This package acts as a zero-dependency, runtime-agnostic port modeled directly on the original Python core library architecture.

It parses complex script transformation configurations (such as EasyReading schemas), structures token match profiles into optimized Directed Trees, and handles deterministic lookups using context-aware validation parameters (including lookbehinds, lookaheads, and boundary lookups).

Features
--------

* **Deterministic Rule Matching:** Automatically orders translation priorities by evaluating matching constraints. Rules requiring the longest match sequences are assigned the lowest traversal costs and evaluated first.
* **Contextual Token Validation:** Complete support for complex rules, including explicit token-matching lookbehinds, token-matching lookaheads, and token-class group boundaries.
* **On-Match Injections:** Supports intermediate injection rules (``onmatch_rules``) to programmatically insert tokens between specific matching classes.
* **Whitespace Pipeline Handling:** Implements automatic token normalization, stripping trailing gaps, and consolidation based on configurable whitespace settings.
* **Modern JavaScript Native Architecture:** Built with strict, type-safe compilation boundaries suitable for Node.js runtimes, bundlers, or frontend web runtimes.

.. note::
   **Unicode String Parsing Gap:** Unlike the Python framework, which interprets Python-specific literal expressions like ``\N{UNICODE CHARACTER NAME}``, the TypeScript port relies entirely on standard ECMAScript Unicode escape formats. Use standard hexadecimal code point sequences (e.g., ``\u0043`` or curly bracket sequences like ``\u{1F600}``) within your rule declarations.

Installation
------------

Install the package into your JavaScript or TypeScript environment using your preferred package manager:

.. code-block:: bash

   $ pnpm add graphtransliterator-ts
   # or using npm / yarn
   $ npm install graphtransliterator-ts

Usage Example
-------------

The following script loads an EasyReading configuration setup, initializes rules containing class lookaheads, and triggers a conversion engine pass.

.. code-block:: typescript

   import {
       fromEasyReadingSettings,
       graphTransliterator,
       transliterate
   } from "graphtransliterator-ts";

   // 1. Declare tokens, classes, and contextual logic rules
   const settings = {
       tokens: {
           "^": ["boundary"],
           "a": ["vowel"],
           "c": ["consonant", "class_c"],
           "$": ["boundary"]
       },
       rules: {
           // Basic mapping execution pass
           "c": "C",
           // Lookahead criteria: target 'a' only when directly followed by class_c
           "a <class_c>": "a_before_class_c"
       },
       whitespace: {
           consolidate: true,
           defaultToken: "^",
           token_class: "boundary"
       }
   };

   // 2. Compile settings into an active graph state tracker instance
   const config = fromEasyReadingSettings(settings);
   const gt = graphTransliterator(config);

   // 3. Process inputs through the compiled framework
   const result = transliterate("ac", gt);
   console.log(result);
   // Returns: "a_before_class_cC"


API Reference
-------------

Initialization Methods
~~~~~~~~~~~~~~~~~~~~~~

``fromEasyReadingSettings(settings)``
    Validates, strips, and converts an EasyReading configuration object format into a clean operational options mapping boundary.

``fromEasyReadingYaml(yamlString)``
    Ingests a raw YAML text configuration block, processing settings parameters directly into an operational parser state tree configuration.

``graphTransliterator(config)``
    Assembles configuration options, class tokens, and boundary matrices into a functioning execution state tree machine.

Runtime Processing Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~

``transliterate(input, gt)``
    Processes a target string through the lowest-cost path of the compiled directed tree and outputs the unified translated text.

``tokenize(input, gt)``
    A helper processing method showing how the internal framework cuts and tags a raw source string into individual structural token elements.

``transliterateReporting(input, gt)``
    Transforms target text and outputs structural trace metadata, defining which rule configurations triggered at which index points for tracking or debugging.


Porting Roadmap & Feature Discrepancies
----------------------------------------

The TypeScript implementation currently provides core transformation and matching algorithms, but does not yet match the full utility suite found in the Python library.

1. **Bundled Profiles:** The Python distribution includes production-ready transliteration profiles like ``Example`` and ``ItransDevanagariToUnicode`` with extensive node-and-edge graph tests. Porting these profiles requires setting up a workspace build task to bundle JSON configurations into the core TypeScript package distribution.
2. **Ambiguity Checks:** The Python initialization validation pipeline can run proactive checks to trigger an ``AmbiguousTransliterationRulesException`` if two identical-cost rules overlap. In TypeScript, users must ensure their configurations are free of overlapping ambiguities prior to compilation.

TypeScript API Reference
------------------------

.. toctree::
   :maxdepth: 3
   :glob:

   typescript_api/*
   typescript_api/classes/*
   typescript_api/functions/*
   typescript_api/interfaces/*
   typescript_api/type-aliases/*
