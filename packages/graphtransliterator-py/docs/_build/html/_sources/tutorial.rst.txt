.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

Tutorial: Using GraphTransliterator
===================================

.. note::

  Python code on this page: :jupyter-download-script:`tutorial` Jupyter Notebook: :jupyter-download-notebook:`tutorial`

Graph Transliterator is designed to allow you to quickly develop rules for
transliterating between languages and scripts. In this tutorial you will use a
portion of Graph Transliterators features, including its token matching,
class-based matching, and on match rules, using the :class:`GraphTransliterator` class.

Tutorial Overview
-----------------

The task for this tutorial will be to design a transliterator
between the  `ITRANS (Indian languages TRANSliteration)
<https://en.wikipedia.org/wiki/ITRANS>`_ encoding for
`Devanagari <https://en.wikipedia.org/wiki/Devanagari>`_ (Hindi) and
standard `Unicode <https://www.unicode.org>`_. ITRANS developed as a means to
transliterate Indic-language using the latin alphabet and punctuation marks
before there were Unicode fonts.

The Devanagari alphabet is an abugida (alphasyllabary), where each "syllable"
is a separate symbol. Vowels, except for the default अ ("a") have a unique
symbol that connects to a consonant. At the start of the words, they have a
unique shape. Consonants in sequence, without intermediary vowels, change
their shape and are joined together. In Unicode, that is accomplished by using
the `Virama <https://en.wikipedia.org/wiki/Virama>`_ character.

Graph Transliterator works by first converting the input text into a series
of tokens. In this tutorial you  will define the tokens of ITRANS and necessary
token classes that will allow us to generate rules for conversion.

Graph Transliterator allows rule matching by preceding tokens, tokens, and
following tokens. It allows token classes to precede or follow any specific
tokens. For this task, you will use a preceding token class to identify when to
write vowel signs as opposed to full vowel characters.

Graph Transliterator also allows the insertion of strings between matches
involving particular token classes. This transliterator will need to
insert the virama character between transliteration rules ending with
consonants in order to create consonant clusters.

Configuring
-----------

Here you will parameterize the Graph Transliterator using its "easy reading"
format, which uses `YAML <https://yaml.org>`_. It maps to a dictionary
containing up to five keys: ``tokens``, ``rules``, ``onmatch_rules``
(optional), ``whitespace``, and ``metadata`` (optional).

Token Definitions
~~~~~~~~~~~~~~~~~

Graph Transliterator tokenizes its input before transliterating. The ``tokens``
section will map the input tokens to their token classes. The main class you
will need is one for consonants, so you can use ``consonant`` as the class.
Graph Transliterator also requires a dedicated whitespace class, so you can use
``whitespace``.

Graph Transliterator allows the use of Unicode character names in files using
\\N{UNICODE CHARACTER NAME HERE}} notation. You can enter the Unicode
characters using that notation or directly. YAML will also unescape \\u####,
where #### is the hexadecimal notation for a character.

Here is a subsection of that definition:

.. code-block:: yaml

  tokens:
    k: [consonant]
    kh: [consonant]
    "\N{LATIN SMALL LETTER N WITH DOT ABOVE}": [consonant]
    a: [vowel]
    aa: [vowel]
    A: [vowel]
    ' ': [wb,whitespace]
    "\t": [wb,whitespace]
    .N: [vowel_sign]

Transliteration Rule Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The rule definitions in Graph Transliterator in "easy reading" format are also
a dictionary where the rules are the key and the production—what should be
outputted by the rule—is the value. For this task, you just need to match
individual tokens and also any preceding token classes:

.. code-block:: yaml

  rules:
    b: \N{DEVANAGARI LETTER B}
    <consonant> A: \N{DEVANAGARI LETTER AA}
    A: \N{DEVANAGARI LETTER AA}

These rules will replace "b" with the devanagari equivalent (ब), and "A" with
with a full letter अा if it is at a start of a word (following a token of class
"wb", for wordbreak) or otherwise with a vowel sign ा if it is not, presumably
following a consonant. Graph Transliterator automatically sorts rules by how
many tokens are required for them to be matched, and it picks the one with
that requires the most tokens. So the "A" following a consonant would be
matched before an "A" after any other character. Graph Transliterator will also
check for ambiguity in these rules, unless ``check_ambiguity`` is set to False.

While not necessary for this tutorial, Graph Transliterator can also
require matching of specific previous or following tokens and also
classes preceding and following those tokens, e.g.

.. code-block:: yaml

  k a r (U M g A <wb>): k,a,r_followed_by_U,M,g,A_and_a_wordbreak
  s o (n a): s,o_followed_by_n,a
  (<wb> p y) aa r: aa,r_preceded_by_a_wordbreak,p,and_y

Here is a subsection of the rules:

.. code-block:: yaml

  rules:
    "\t": "\t"
    ' ': ' '
    ',': ','
    .D: "\N{DEVANAGARI LETTER DDDHA}"
    <consonant> A: "\N{DEVANAGARI VOWEL SIGN AA}"
    "\N{LATIN SMALL LETTER N WITH DOT ABOVE}": "\N{DEVANAGARI LETTER NGA}"

On Match Rule Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~
You will want to insert the Virama character between consonants so that they
will join together in Unicode output. To do so, add an "onmatch_rules"
section:

.. code-block:: yaml

  onmatch_rules:
    - <consonant> + <consonant>: "\N{DEVANAGARI SIGN VIRAMA}"

Unlike the tokens and rules, the *onmatch rules are ordered*. The first rule
matched is applied. In YAML, they consist of a list of dictionaries each with a
single key and value. The value is the production string to be inserted between
matches. The ` + ` represents that space. So in the input string `kyA`, which
would tokenize as :obj:`[' ','k','y','A',' ']`, a virama character would be
inserted when `y` is matched, as it is of class "consonant" and the previously
matched transliteration rule for "k" ends with a "consonant".

Whitespace Definitions
~~~~~~~~~~~~~~~~~~~~~~
The final required setup parameter is for whitespace. These include the
``default`` whitespace token, which is temporarily added before and after the
input tokens; the ``consolidate`` option to replace sequential whitespace
characters with a single default whitespace character; and the ``token_class``
of whitespace tokens:

.. code-block:: yaml

  whitespace:
    consolidate: false
    default: ' '
    token_class: whitespace

Metadata Definitions
~~~~~~~~~~~~~~~~~~~~
Graph Transliterator also allows metadata to be added to its settings:

.. code-block:: yaml

  metadata:
    title: "ITRANS Devanagari to Unicode"
    version: "0.1.0"

Creating a Transliterator
-------------------------
Now that the settings are ready, you can create a Graph Transliterator.
Since you have  been using the "easy reading" format, you
can use :meth:`GraphTransliterator.from_yaml_file` to read from a
specific file or the :meth:`GraphTransliterator.from_yaml` to read from a
YAML string. You read from the loaded contents of an "easy reading"
YAML file using :meth:`GraphTransliterator.from_dict`. Graph Transliterator
will convert those settings into basic Python types and then return a
:obj:`GraphTransliterator`:

.. jupyter-execute::

    from graphtransliterator import GraphTransliterator
    easyreading_yaml = """
    tokens:
      k: [consonant]
      kh: [consonant]
      g: [consonant]
      gh: [consonant]
      ~N: [consonant]
      "\N{LATIN SMALL LETTER N WITH DOT ABOVE}": [consonant]
      ch: [consonant]
      chh: [consonant]
      Ch: [consonant]
      j: [consonant]
      jh: [consonant]
      ~n: [consonant]
      T: [consonant]
      Th: [consonant]
      D: [consonant]
      Dh: [consonant]
      N: [consonant]
      t: [consonant]
      th: [consonant]
      d: [consonant]
      dh: [consonant]
      n: [consonant]
      ^n: [consonant]
      p: [consonant]
      ph: [consonant]
      b: [consonant]
      bh: [consonant]
      m: [consonant]
      y: [consonant]
      r: [consonant]
      R: [consonant]
      l: [consonant]
      ld: [consonant]
      L: [consonant]
      zh: [consonant]
      v: [consonant]
      sh: [consonant]
      Sh: [consonant]
      s: [consonant]
      h: [consonant]
      x: [consonant]
      kSh: [consonant]
      GY: [consonant]
      j~n: [consonant]
      dny: [consonant]
      q: [consonant]
      K: [consonant]
      G: [consonant]
      J: [consonant]
      z: [consonant]
      .D: [consonant]
      .Dh: [consonant]
      f: [consonant]
      Y: [consonant]
      a: [vowel]
      aa: [vowel]
      A: [vowel]
      i: [vowel]
      ii: [vowel]
      I: [vowel]
      ee: [vowel]
      u: [vowel]
      uu: [vowel]
      U: [vowel]
      RRi: [vowel]
      R^i: [vowel]
      LLi: [vowel]
      L^i: [vowel]
      RRI: [vowel]
      LLI: [vowel]
      a.c: [vowel]
      ^e: [vowel]
      e: [vowel]
      ai: [vowel]
      A.c: [vowel]
      ^o: [vowel]
      o: [vowel]
      au: [vowel]
      ' ': [wb,whitespace]
      "\t": [wb,whitespace]
      ',': [wb]
      .h: [wb]
      H: [wb]
      OM: [wb]
      AUM: [wb]
      '|': [wb]
      '||': [wb]
      '0': [wb]
      '1': [wb]
      '2': [wb]
      '3': [wb]
      '4': [wb]
      '5': [wb]
      '6': [wb]
      '7': [wb]
      '8': [wb]
      '9': [wb]
      Rs.: [wb]
      ~Rs.: [wb]
      .a: [wb]
      a.e: [vowel_sign]
      .N: [vowel_sign]
      .n: [vowel_sign]
      M: [vowel_sign]
      .m: [vowel_sign]
    rules:
      "\t": "\t"
      ' ': ' '
      ',': ','
      .D: "\N{DEVANAGARI LETTER DDDHA}"
      .Dh: "\N{DEVANAGARI LETTER RHA}"
      .N: "\N{DEVANAGARI SIGN CANDRABINDU}"
      .a: "\N{DEVANAGARI SIGN AVAGRAHA}"
      .h: "\N{DEVANAGARI SIGN VIRAMA}\N{ZERO WIDTH NON-JOINER}"
      .m: "\N{DEVANAGARI SIGN ANUSVARA}"
      .n: "\N{DEVANAGARI SIGN ANUSVARA}"
      '0': "\N{DEVANAGARI DIGIT ZERO}"
      '1': "\N{DEVANAGARI DIGIT ONE}"
      '2': "\N{DEVANAGARI DIGIT TWO}"
      '3': "\N{DEVANAGARI DIGIT THREE}"
      '4': "\N{DEVANAGARI DIGIT FOUR}"
      '5': "\N{DEVANAGARI DIGIT FIVE}"
      '6': "\N{DEVANAGARI DIGIT SIX}"
      '7': "\N{DEVANAGARI DIGIT SEVEN}"
      '8': "\N{DEVANAGARI DIGIT EIGHT}"
      '9': "\N{DEVANAGARI DIGIT NINE}"
      <consonant> A: "\N{DEVANAGARI VOWEL SIGN AA}"
      <consonant> A.c: "\N{DEVANAGARI VOWEL SIGN CANDRA O}"
      <consonant> I: "\N{DEVANAGARI VOWEL SIGN II}"
      <consonant> LLI: "\N{DEVANAGARI VOWEL SIGN VOCALIC LL}"
      <consonant> LLi: "\N{DEVANAGARI VOWEL SIGN VOCALIC L}"
      <consonant> L^i: "\N{DEVANAGARI VOWEL SIGN VOCALIC L}"
      <consonant> RRI: "\N{DEVANAGARI VOWEL SIGN VOCALIC RR}"
      <consonant> RRi: "\N{DEVANAGARI VOWEL SIGN VOCALIC R}"
      <consonant> R^i: "\N{DEVANAGARI VOWEL SIGN VOCALIC R}"
      <consonant> U: "\N{DEVANAGARI VOWEL SIGN UU}"
      <consonant> ^e: "\N{DEVANAGARI VOWEL SIGN SHORT E}"
      <consonant> ^o: "\N{DEVANAGARI VOWEL SIGN SHORT O}"
      <consonant> a: ''
      <consonant> a.c: "\N{DEVANAGARI VOWEL SIGN CANDRA E}"
      <consonant> aa: "\N{DEVANAGARI VOWEL SIGN AA}"
      <consonant> ai: "\N{DEVANAGARI VOWEL SIGN AI}"
      <consonant> au: "\N{DEVANAGARI VOWEL SIGN AU}"
      <consonant> e: "\N{DEVANAGARI VOWEL SIGN E}"
      <consonant> ee: "\N{DEVANAGARI VOWEL SIGN II}"
      <consonant> i: "\N{DEVANAGARI VOWEL SIGN I}"
      <consonant> ii: "\N{DEVANAGARI VOWEL SIGN II}"
      <consonant> o: "\N{DEVANAGARI VOWEL SIGN O}"
      <consonant> u: "\N{DEVANAGARI VOWEL SIGN U}"
      <consonant> uu: "\N{DEVANAGARI VOWEL SIGN UU}"
      A: "\N{DEVANAGARI LETTER AA}"
      A.c: "\N{DEVANAGARI LETTER CANDRA O}"
      AUM: "\N{DEVANAGARI OM}"
      Ch: "\N{DEVANAGARI LETTER CHA}"
      D: "\N{DEVANAGARI LETTER DDA}"
      Dh: "\N{DEVANAGARI LETTER DDHA}"
      G: "\N{DEVANAGARI LETTER GHHA}"
      GY: "\N{DEVANAGARI LETTER JA}\N{DEVANAGARI SIGN VIRAMA}\N{DEVANAGARI LETTER NYA}"
      H: "\N{DEVANAGARI SIGN VISARGA}"
      I: "\N{DEVANAGARI LETTER II}"
      J: "\N{DEVANAGARI LETTER ZA}"
      K: "\N{DEVANAGARI LETTER KHHA}"
      L: "\N{DEVANAGARI LETTER LLA}"
      LLI: "\N{DEVANAGARI LETTER VOCALIC LL}"
      LLi: "\N{DEVANAGARI LETTER VOCALIC L}"
      L^i: "\N{DEVANAGARI LETTER VOCALIC L}"
      M: "\N{DEVANAGARI SIGN ANUSVARA}"
      N: "\N{DEVANAGARI LETTER NNA}"
      OM: "\N{DEVANAGARI OM}"
      R: "\N{DEVANAGARI LETTER RRA}"
      RRI: "\N{DEVANAGARI LETTER VOCALIC RR}"
      RRi: "\N{DEVANAGARI LETTER VOCALIC R}"
      R^i: "\N{DEVANAGARI LETTER VOCALIC R}"
      Rs.: "\N{INDIAN RUPEE SIGN}"
      Sh: "\N{DEVANAGARI LETTER SSA}"
      T: "\N{DEVANAGARI LETTER TTA}"
      Th: "\N{DEVANAGARI LETTER TTHA}"
      U: "\N{DEVANAGARI LETTER UU}"
      Y: "\N{DEVANAGARI LETTER YYA}"
      ^e: "\N{DEVANAGARI LETTER SHORT E}"
      ^n: "\N{DEVANAGARI LETTER NNNA}"
      ^o: "\N{DEVANAGARI LETTER SHORT O}"
      a: "\N{DEVANAGARI LETTER A}"
      a.c: "\N{DEVANAGARI LETTER CANDRA E}"
      a.e: "\N{DEVANAGARI LETTER CANDRA A}"
      aa: "\N{DEVANAGARI LETTER AA}"
      ai: "\N{DEVANAGARI LETTER AI}"
      au: "\N{DEVANAGARI LETTER AU}"
      b: "\N{DEVANAGARI LETTER BA}"
      bh: "\N{DEVANAGARI LETTER BHA}"
      ch: "\N{DEVANAGARI LETTER CA}"
      chh: "\N{DEVANAGARI LETTER CHA}"
      d: "\N{DEVANAGARI LETTER DA}"
      dh: "\N{DEVANAGARI LETTER DHA}"
      dny: "\N{DEVANAGARI LETTER JA}\N{DEVANAGARI SIGN VIRAMA}\N{DEVANAGARI LETTER NYA}"
      e: "\N{DEVANAGARI LETTER E}"
      ee: "\N{DEVANAGARI LETTER II}"
      f: "\N{DEVANAGARI LETTER FA}"
      g: "\N{DEVANAGARI LETTER GA}"
      gh: "\N{DEVANAGARI LETTER GHA}"
      h: "\N{DEVANAGARI LETTER HA}"
      i: "\N{DEVANAGARI LETTER I}"
      ii: "\N{DEVANAGARI LETTER II}"
      j: "\N{DEVANAGARI LETTER JA}"
      jh: "\N{DEVANAGARI LETTER JHA}"
      j~n: "\N{DEVANAGARI LETTER JA}\N{DEVANAGARI SIGN VIRAMA}\N{DEVANAGARI LETTER NYA}"
      k: "\N{DEVANAGARI LETTER KA}"
      kSh: "\N{DEVANAGARI LETTER KA}\N{DEVANAGARI SIGN VIRAMA}\N{DEVANAGARI LETTER SSA}"
      kh: "\N{DEVANAGARI LETTER KHA}"
      l: "\N{DEVANAGARI LETTER LA}"
      ld: "\N{DEVANAGARI LETTER LLA}"
      m: "\N{DEVANAGARI LETTER MA}"
      n: "\N{DEVANAGARI LETTER NA}"
      o: "\N{DEVANAGARI LETTER O}"
      p: "\N{DEVANAGARI LETTER PA}"
      ph: "\N{DEVANAGARI LETTER PHA}"
      q: "\N{DEVANAGARI LETTER QA}"
      r: "\N{DEVANAGARI LETTER RA}"
      s: "\N{DEVANAGARI LETTER SA}"
      sh: "\N{DEVANAGARI LETTER SHA}"
      t: "\N{DEVANAGARI LETTER TA}"
      th: "\N{DEVANAGARI LETTER THA}"
      u: "\N{DEVANAGARI LETTER U}"
      uu: "\N{DEVANAGARI LETTER UU}"
      v: "\N{DEVANAGARI LETTER VA}"
      x: "\N{DEVANAGARI LETTER KA}\N{DEVANAGARI SIGN VIRAMA}\N{DEVANAGARI LETTER SSA}"
      y: "\N{DEVANAGARI LETTER YA}"
      z: "\N{DEVANAGARI LETTER ZA}"
      zh: "\N{DEVANAGARI LETTER LLLA}"
      '|': "\N{DEVANAGARI DANDA}"
      '||': "\N{DEVANAGARI DOUBLE DANDA}"
      ~N: "\N{DEVANAGARI LETTER NGA}"
      ~Rs.: "\N{INDIAN RUPEE SIGN}"
      ~n: "\N{DEVANAGARI LETTER NYA}"
      "\N{LATIN SMALL LETTER N WITH DOT ABOVE}": "\N{DEVANAGARI LETTER NGA}"
    onmatch_rules:
    - <consonant> + <consonant>: "\N{DEVANAGARI SIGN VIRAMA}"
    whitespace:
      consolidate: false
      default: ' '
      token_class: whitespace
    metadata:
      title: ITRANS to Unicode
      version: 0.1.0
    """
    gt = GraphTransliterator.from_yaml(easyreading_yaml)

Transliterating
---------------
With the transliterator created, you can now transliterate using
:meth:`GraphTransliterator.transliterate`:

.. jupyter-execute::

    gt.transliterate("aaj mausam ba.Daa beiimaan hai, aaj mausam")

Other Information
-----------------
Graph Transliterator has a few other tools built in that are for more
specialized applications.

If you want to  receive the details of the most recent transliteration, access
:attr:`GraphTransliterator.last_matched_rules` to get this list of rules
matched:

.. jupyter-execute::

    gt.last_matched_rules

Or if you just want to know the tokens matched by each rule, check
:attr:`GraphTransliterator.last_matched_rule_tokens`:

.. jupyter-execute::

    gt.last_matched_rule_tokens


You can access the directed tree used by GraphTransliterator using
:attr:`GraphTransliterator.graph`:

.. jupyter-execute::

    gt.graph
