.. -------------------------------------------------------------------------------------
.. Note:
..     This is a documentation source file for Graph Transliterator.
..     Certain links and other features will not be accessible from here.
.. Links:
..     - Documentation: https://graphtransliterator.readthedocs.org
..     - PyPI: https://pypi.org/project/graphtransliterator/
..     - Repository: https://github.com/seanpue/graphtransliterator/
.. -------------------------------------------------------------------------------------

=====
Usage
=====


.. note:

  Python code on this page: :jupyter-download-script:`usage` Jupyter Notebook: :jupyter-download-notebook:`usage`

To use Graph Transliterator in a project:

.. jupyter-execute::

  from graphtransliterator import GraphTransliterator

Overview
========
Graph Transliterator requires that you first configure a :class:`GraphTransliterator`.
Then you can transliterate an input string using :meth:`transliterate`. There are a few
additional methods that can be used to extract information for specific use cases, such
as details about which rules were matched.

Configuration
=============

Graph Transliterator takes the following parameters:

  1. The acceptable types of **tokens** in the input string as well as any
     associated **token classes**.
  2. The **transliteration rules** for the transformation of the input string.
  3. Rules for dealing with **whitespace**.
  4. **"On match" rules** for strings to be inserted in particular contexts
     right before a transliteration rule's output is added (optional).
  5. **Metadata** settings for the transliterator (optional).

Initialization
--------------

Defining the rules for transliteration can be difficult, especially when dealing with
complex scripts. That is why Graph Transliterator uses an "easy reading" format that
allows you to enter the transliteration rules in the popular `YAML <https://yaml.org/>`_
format, either from a string (using :func:`from_yaml`) or by reading
from a file or stream (:func:`GraphTransliterator.from_yaml_file`). You can also
initialize from the loaded contents of YAML
(:func:`GraphTransliterator.from_easyreading_dict`).

Here is a quick sample that parameterizes :class:`GraphTransliterator` using an easy
reading YAML string (with comments):

.. jupyter-execute::

  yaml_ = """
    tokens:
      a: [vowel]               # type of token ("a") and its class (vowel)
      bb: [consonant, b_class] # type of token ("bb") and its classes (consonant, b_class)
      ' ': [wb]                # type of token (" ") and its class ("wb", for wordbreak)
    rules:
      a: A       # transliterate "a" to "A"
      bb: B      # transliterate "bb" to "B"
      a a: <2AS> # transliterate ("a", "a") to "<2AS>"
      ' ': ' '   # transliterate ' ' to ' '
    whitespace:
      default: " "        # default whitespace token
      consolidate: false  # whitespace should not be consolidated
      token_class: wb     # whitespace token class
  """
  gt_one = GraphTransliterator.from_yaml(yaml_)
  gt_one.transliterate('a')

.. jupyter-execute::

  gt_one.transliterate('bb')

.. jupyter-execute::

  gt_one.transliterate('aabb')


The example above shows a very simple transliterator that replaces the input token "a"
with "A", "bb" with "B", " " with " ", and two "a" in a row with "<2AS>". It does not
consolidate whitespace, and treats " " as its default whitespace token. Tokens contain
strings of one or more characters.

Input Tokens and Token Class Settings
-------------------------------------
During transliteration, Graph Transliterator first attempts to convert the input string
into a list of tokens. This is done internally using
:meth:`GraphTransliterator.tokenize`:

.. jupyter-execute::

  gt_one.tokenize('abba')


Note that the default whitespace  token is added to the start and end of the input
tokens.

Tokens can be more than one character, and longer tokens are matched first:

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      a: []      # "a" token with no classes
      aa: []     # "aa" token with no classes
      ' ': [wb]  # " " token and its class ("wb", for wordbreak)
    rules:
      aa: <DOUBLE_A>  # transliterate "aa" to "<DOUBLE_A>"
      a: <SINGLE_A>   # transliterate "a" to "<SINGLE_A>"
    whitespace:
      default: " "        # default whitespace token
      consolidate: false  # whitespace should not be consolidated
      token_class: wb     # whitespace token class
  """
  gt_two = GraphTransliterator.from_yaml(yaml_)
  gt_two.transliterate('a')

.. jupyter-execute::

  gt_two.transliterate('aa')

.. jupyter-execute::

  gt_two.transliterate('aaa')


Here the input "aaa" is transliterated as "<DOUBLE_A><SINGLE_A>", as the longer token
"aa" is matched before "a".

Tokens can be assigned zero or more classes. Each class is a string of your choice.
These classes are used in transliteration rules. In YAML they are defined as a
dictionary, but internally the rules are stored as a dictionary of token strings keyed
to a set of token classes. They can be accessed using
:attr:`GraphTransliterator.tokens`:

.. jupyter-execute::

  gt_two.tokens


Transliteration Rules
---------------------
Graph Transliterator can handle a variety of transliteration tasks. To do so, it uses
transliteration rules that contain **match settings** for particular tokens in specific
contexts and also a resulting **production**, or string to be appended to the output
string.

Match Settings
~~~~~~~~~~~~~~
Transliteration rules contain the following parameters (ordered by where they would
appear in a list of tokens):

  - **previous token classes** : a list of token classes (optional)
  - **previous tokens** : a list of tokens (optional)
  - **tokens** : a list of tokens
  - **next tokens** : a list of tokens (optional)
  - **next token classes** : a list of token classes (optional)

One or more (**tokens**) must be matched in a particular location. However, specific
tokens can be required before (**previous tokens**) or behind (**next tokens**) those
tokens. Additionally, particular token classes can be required before (**previous token
classes**) and behind (**next token classes**) all of the specific tokens required
(previous tokens, tokens, next tokens).

Depending on their complexity, these match conditions can be entered using the "easy
reading" format in the following ways.

If there are no required lookahead or lookbehind tokens, the rule can be as follows:

.. code-block:: yaml

  rules:
     a a: aa  # two tokens (a,a), with production "production_aa"

If, in an addition to tokens, there are specific previous or following tokens that must
be matched, the rule can be entered as:

.. code-block:: yaml

  tokens:
    a: []
    b: []
    c: []
    d: []
  rules:
     a (b): a_before_b  # matches  token 'a' with the next token 'b'
     (c) a: a_after_c   # matches token 'a' when the previous token is 'c'
     a (b c): a_before_b_and_c # matches token 'a' when next tokens are 'b' then 'c'
     (d) a (b c): a_after_d_and_before_b,c  # matches the token 'a' after 'd' and before 'b' and 'c'

Token class names are indicated between angular brackets ("<classname>"). If preceding
and following tokens are not required but classes are, these can be entered as follows:

.. code-block:: yaml

  tokens:
    a: []
    b: [class_b]
    c: []
    ' ': [wb]
  rules:
    c <class_b>: c_after _class_b  # match token 'c' before a token of class 'class_b`
    <class_b> a: a_before_class_b  # match token 'a' after a token of class `class_b`
    <class_b> a <class_b>: a_between_class_b #  match token 'a' between tokens of class 'class_b'

If token classes must precede or follow specific tokens, these can be entered as:

.. code-block:: yaml

  tokens:
    a: []
    b: []
    c: [class_c]
    d: [class_d]
    ' ': [wb]
  rules:
    d (b <class_c>): a_before_b_and_class_c # match token 'd' before 'b' and a token of class 'class_c'
    (<class_c> b) a: a_after_b_and_class_c  # match token 'a' after 'b' and a token of class 'class_c'
    (<class_c> d) a (b <class_c> <class_d>): x # match 'a' after token of 'class_c' and 'd' and before a token of 'class_c' and of 'class_d'
  whitespace:
    default: ' '
    token_class: wb
    consolidate: false

Automatic Ordering of Transliteration Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graph Transliterator automatically orders the transliteration rules based on the number
of tokens required by the rule. It *picks the rule requiring the longest match in a
given context*. It does so by assigning a cost to each transliteration rule that
decreases depending on the number of tokens required by the rule. More tokens decreases
the cost of a rule causing it to be matched first:

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      a: []
      b: []
      c: [class_of_c]
      ' ': [wb]
    rules:
      a: <<A>>
      a b: <<AB>>
      b: <<B>>
      c: <<C>>
      ' ': _
      <class_of_c> a b: <<AB_after_C>>
    whitespace:
      default: " "
      consolidate: false
      token_class: wb
  """
  gt_three = GraphTransliterator.from_yaml(yaml_)
  gt_three.transliterate("ab")  # should match rule "a b"

.. jupyter-execute::

  gt_three.transliterate("cab") # should match rules: "c", and "<class_of_c> a b"


Internally, Graph Transliterator uses a special :class:`TransliterationRule` class.
These can be accessed using :attr:`GraphTransliterator.rules`. Rules are sorted by cost,
lowest to highest:

.. jupyter-execute::

  gt_three.rules



Whitespace Settings
-------------------
Whitespace is often very important in transliteration tasks, as the form of many letters
may change at the start or end of words, as in the right-to-left Perso-Arabic and
left-to-right Indic scripts. Therefore, Graph Transliterator requires the following
**whitespace settings**:

- the **default** whitespace token
- the whitespace **token class**
- whether or not to **consolidate** whitespace

*A whitespace token and token class must be defined for any Graph Transliterator*. A
whitespace character is added temporarily to the start and end of the input tokens
during the transliteration process.

The ``consolidate`` option may be useful in particular transliteration tasks. It
replaces any sequential whitespace tokens in the input string with the default
whitespace character. At the start and end of input, it removes any whitespace:

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      a: []
      ' ': [wb]
    rules:
      <wb> a: _A
      a <wb>: A_
      <wb> a <wb>: _A_
      a: a
      ' ': ' '
    whitespace:
      default: " "        # default whitespace token
      consolidate: true   # whitespace should be consolidated
      token_class: wb     # whitespace token class
  """
  gt = GraphTransliterator.from_yaml(yaml_)
  gt.transliterate('a')   # whitespace present at start of string

.. jupyter-execute::

  gt.transliterate('aa')  # whitespace present at start and end of string

.. jupyter-execute::

  gt.transliterate(' a')  # consolidate removes whitespace at start of string

.. jupyter-execute::

  gt.transliterate('a ')  # consolidate removes whitespace at end of string


Whitespace settings are stored internally as :class:`WhitespaceRules` and can be
accessed using :attr:`GraphTransliterator.whitespace`:

.. jupyter-execute::

  gt.whitespace


On Match Rules
--------------
Graph Transliterator allows strings to be inserted right
before the productions of transliteration rules. These take as parameters:

- a list of **previous token classes**, preceding the location of the transliteration
  rule match
- a list of **next token classes**, from the index of the transliteration rule match
- a **production** string to insert

In the easy reading YAML format, the :obj:`onmatch_rules` are a list of dictionaries.
The key consists of the token class names in angular brackets ("<classname>"), and the
previous classes to match are separated from the following classes by a "+". The
production is the value of the dictionary:

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      a: [vowel]
      ' ': [wb]
    rules:
      a: A
      ' ': ' '
    whitespace:
      default: " "
      consolidate: false
      token_class: wb
    onmatch_rules:
      - <vowel> + <vowel>: ',' # add a comma between vowels
   """
  gt = GraphTransliterator.from_yaml(yaml_)
  gt.transliterate('aa')


On Match rules are stored internally as a :class:`OnMatchRule` and can be accessed using
:attr:`GraphTransliterator.onmatch_rules`:

.. jupyter-execute::

  gt.onmatch_rules



Metadata
--------
Graph Transliterator allows for the storage of metadata as another input parameter,
``metadata``. It is a dictionary, and fields can be added to it:

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      a: []
      ' ': [wb]
    rules:
      a: A
      ' ': ' '
    whitespace:
      default: " "
      consolidate: false
      token_class: wb
    metadata:
      author: Author McAuthorson
      version: 0.1.1
      description: A sample Graph Transliterator
    """
  gt = GraphTransliterator.from_yaml(yaml_)
  gt.metadata


Unicode Support
---------------
Graph Transliterator allows Unicode characters to be specified by name, including in
YAML files, using the format "\\N{UNICODE CHARACTER NAME}" or "\\u{####}" (where #### is
the hexadecimal character code):

.. jupyter-execute::
  :linenos:

  yaml_ = """
    tokens:
      b: []
      c: []
      ' ': [wb]
    rules:
      b: \N{LATIN CAPITAL LETTER B}
      c: \u0043    # hexadecimal Unicode character code for 'C'
      ' ': ' '
    whitespace:
      default: " "
      consolidate: false
      token_class: wb
    """
  gt = GraphTransliterator.from_yaml(yaml_)
  gt.transliterate('b')

.. jupyter-execute::

  gt.transliterate('c')


Configuring Directly
--------------------
In addition to using :meth:`GraphTansliterator.from_yaml` and
:meth:`GraphTransliterator.from_yaml_file`, Graph Transliterator can also be configured
and initialized directly using basic Python types passed as dictionary to
:meth:`GraphTransliterator.from_dict`

.. jupyter-execute::
  :linenos:

  settings = {
    'tokens': {'a': ['vowel'],
               ' ': ['wb']},
    'rules': [
        {'production': 'A', 'tokens': ['a']},
        {'production': ' ', 'tokens': [' ']}],
    'onmatch_rules': [
        {'prev_classes': ['vowel'],
         'next_classes': ['vowel'],
         'production': ','}],
    'whitespace': {
        'default': ' ',
        'consolidate': False,
        'token_class': 'wb'},
    'metadata': {
        'author': 'Author McAuthorson'}
  }
  gt = GraphTransliterator.from_dict(settings)
  gt.transliterate('a')


This feature can be useful if generating a Graph Transliterator using code as opposed to
a configuration file.

Ambiguity Checking
------------------
Graph Transliterator, by default, will check for ambiguity in its transliteration rules.
If two rules of the same cost would match the same string(s) and those strings would not
be matched by a less costly rule, an :exc:`AmbiguousTransliterationRulesException`
occurs. Details of all exceptions will be reported as a :meth:`logging.warning`:

.. jupyter-execute::
  :hide-code:
  :hide-output:

  %xmode Minimal

.. jupyter-execute::
  :raises: AmbiguousTransliterationRulesException
  :stderr:
  :linenos:

  yaml_ = """
  tokens:
    a: [class1, class2]
    b: []
    ' ': [wb]
  rules:
    <class1> a: A
    <class2> a: AA # ambiguous rule
    <class1> b: BB
    b <class2>: BB # also ambiguous
  whitespace:
    default: ' '
    consolidate: True
    token_class: wb
  """
  gt = GraphTransliterator.from_yaml(yaml_)

The warning shows the set of possible previous tokens, matched tokens, and next tokens
as three sets.

Ambiguity checking is only necessary when using an untested Graph Transliterator. It can
be turned off during initialization. To do so, set the initialization parameter
:obj:`check_ambiguity` to `False`.

Ambiguity checking can also be done on demand using :meth:`check_for_ambiguity`.

Ambiguity checking is not performed if loading from a serialized GraphTransliterator
using :meth:`GraphTransliterator.load` or :meth:`GraphTransliterator.loads`.

Setup Validation
----------------
Graph Transliterator validates both the "easy reading" configuration and the direct
configuration using the :py:mod:`marshmallow` library.

Transliteration and Its Exceptions
==================================

The main method of Graph Transliterator is
:meth:`GraphTransliterator.transliterate`. It will return a string:

.. jupyter-execute::
  :raises: AmbiguousTransliterationRulesException
  :stderr:
  :linenos:

  GraphTransliterator.from_yaml(
  '''
  tokens:
    a: []
    ' ': [wb]
  rules:
    a: A
    ' ': '_'
  whitespace:
    default: ' '
    consolidate: True
    token_class: wb
  ''').transliterate("a a")


Details of transliteration error exceptions will be logged using
:meth:`logging.warning`.

Unrecognizable Input Token
--------------------------

Unless the :class:`GraphTransliterator` is initialized with or has the property
:obj:`ignore_errors` set as :obj:`True`, :meth:`GraphTransliterator.transliterate` will
raise :exc:`UnrecognizableInputTokenException` when character(s) in the input string do
not correspond to any defined types of input tokens. In both cases, there will be a
:meth:`logging.warning`:

.. jupyter-execute::
  :raises: UnrecognizableInputTokenException
  :stderr:
  :linenos:

  from graphtransliterator import GraphTransliterator
  yaml_ = """
    tokens:
     a: []
     ' ': [wb]
    rules:
      a: A
      ' ': ' '
    whitespace:
      default: " "
      consolidate: true
      token_class: wb
  """
  GraphTransliterator.from_yaml(yaml_).transliterate("a!a") # ignore_errors=False


.. jupyter-execute::
  :linenos:
  :stderr:

  GraphTransliterator.from_yaml(yaml_, ignore_errors=True).transliterate("a!a") # ignore_errors=True

No Matching Transliteration Rule
--------------------------------

Another possible error occurs when no transliteration rule can be identified at a
particular index in the index string. In that case, there will be a
:meth:`logging.warning`. If the parameter :obj:`ignore_errors` is set to :obj:`True`,
the token index will be advanced. Otherwise, there will be a
:exc:`NoMatchingTransliterationRuleException`:

.. jupyter-execute::
  :raises: NoMatchingTransliterationRuleException
  :stderr:
  :linenos:

  yaml_='''
    tokens:
      a: []
      b: []
      ' ': [wb]
    rules:
      a: A
      b (a): B
    whitespace:
      default: ' '
      token_class: wb
      consolidate: False
  '''
  gt = GraphTransliterator.from_yaml(yaml_)
  gt.transliterate("ab")

.. jupyter-execute::
  :stderr:

  gt.ignore_errors = True
  gt.transliterate("ab")

Additional Methods
==================

Graph Transliterator also offers a few additional methods that may be useful for
particular tasks.

Serialization and Deserialization
---------------------------------

The settings of a Graph Transliterator can be serialized using
:meth:`GraphTransliterator.dump`, which returns a dictionary of native Python data
types. A JSON string of the same can be accessed using
:meth:`GraphTransliterator.dumps`. Validation is not performed during a dump.

By default, :meth:`GraphTransliterator.dumps` will use compression level 2, which
removes the internal graph and indexes tokens and graph node labels. Compression level 1
also indexes tokens and graph node labels and contains the graph. Compression level 0
is human readable and includes the graph. No information is lost during compression.
Level 2, the default, loads the fastest and also has the smallest file size.

A GraphTransliterator can be loaded from serialized settings, e.g. in an API context,
using :meth:`GraphTransliterator.load` and from JSON data as
:meth:`GraphTransliterator.loads`. Because they are intended to be quick, neither method
performs ambiguity checks or strict validation checking by default.

Serialization can be useful if providing an API or making the configured Graph
Transliterator available in other programming languages, e.g. Javascript.

Matching at an Index
--------------------

The method :meth:`match_at` is also public. It matches the best transliteration rule at
a particular index, which is the rule that contains the largest number of required
tokens. The method also has the option :obj:`match_all` which, if set, returns all
possible transliteration matches at a particular location:

.. jupyter-execute::
  :linenos:

  gt = GraphTransliterator.from_yaml('''
          tokens:
              a: []
              a a: []
              ' ': [wb]
          rules:
              a: <A>
              a a: <AA>
          whitespace:
              default: ' '
              consolidate: True
              token_class: wb
  ''')
  tokens = gt.tokenize("aa")
  tokens # whitespace added to ends

.. jupyter-execute::

  gt.match_at(1, tokens) # returns index to rule

.. jupyter-execute::

  gt.rules[gt.match_at(1, tokens)] # actual rule

.. jupyter-execute::

  gt.match_at(1, tokens, match_all=True) # index to rules, with match_all

.. jupyter-execute::

  [gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)] # actual rules, with match_all


Details of Matches
------------------

Each Graph Transliterator has a property :attr:`last_matched_rules` which returns a list
of :obj:`TransliterationRule` of the previously matched transliteration rules:

.. jupyter-execute::
  :linenos:

  gt.transliterate("aaa")

.. jupyter-execute::

  gt.last_matched_rules


The particular tokens matched by those rules can be accessed using
:attr:`last_matched_rule_tokens`:

.. jupyter-execute::

  gt.last_matched_rule_tokens


Pruning of Rules
----------------

In particular cases, it may be useful to remove certain transliteration rules from a
more robustly defined Graph Transliterator based on the string output produced by the
rules. That can be done using :meth:`pruned_of`:

.. jupyter-execute::
  :linenos:

  gt.rules

.. jupyter-execute::

  gt.pruned_of('<AA>').rules

.. jupyter-execute::

  gt.pruned_of(['<A>', '<AA>']).rules


Internal Graph
==============
Graph Transliterator creates a directed tree during its initialization. During calls to
:meth:`transliterate`, it searches that graph to find the best transliteration match at
a particular index in the tokens of the input string.

DirectedGraph
-------------

The tree is an instance of :class:`DirectedGraph` that can be accessed using
:attr:`GraphTransliterator.graph`. It contains: a list of nodes, each consisting of a
dictionary of attributes; a dictionary of edges keyed between the head and tail of an
edge that contains a dictionary of edge attributes; and finally an edge list.

.. jupyter-execute::
  :linenos:

  gt = GraphTransliterator.from_yaml(
      """
      tokens:
        a: []
        ' ': [wb]
      rules:
        a: b
        <wb> a: B
        ' ': ' '
      whitespace:
        token_class: wb
        default: ' '
        consolidate: false
      """)
  gt.graph


Nodes
-----

The tree has nodes of three types: `Start`, `token`, and `rule`. A single `Start` node,
the root, is connected to all other nodes. A `token` node corresponds to a token having
been matched. Finally, `rule` nodes are leaf nodes (with no outgoing edges) that
correspond to matched transliteration rules:

.. jupyter-execute::

  gt.graph.node


Edges
-----

Edges between these nodes may have different constraints in their attributes:

.. jupyter-execute::

  gt.graph.edge


Before the `token` nodes, there is a `token` constraint on the edge that must be matched
before the transliterator can visit the token node:

.. jupyter-execute::

  gt.graph.edge[0][1]


On the edges before rules there may be other `constraints`, such as certain tokens
preceding or following tokens of the corresponding transliteration rule:

.. jupyter-execute::

  gt.graph.edge[1][2]


An edge list is also maintained that consists of a tuple of (head, tail):

.. jupyter-execute::

  gt.graph.edge_list


Search and Preprocessing
------------------------

Graph Transliterator uses a best-first search, implemented using a stack, that finds the
transliteration with the the lowest cost. The cost function is:

.. math::

  \text{cost}(rule) = \log_2{\big(1+\frac{1}{1+\text{count}\_\text{of}\_ \text{tokens}\_ \text{in}(rule)}\big)}

It results in a number between 1 and 0 that lessens as more tokens must be matched. Each
edge on the graph has a cost attribute that is set to the lowest cost transliteration
rule following it. When transliterating, Graph Transliterator will try lower cost edges
first and will backtrack if the constraint conditions are not met.

.. _sample_graph:
.. figure:: _static/figure1.png
   :alt: Sample graph

   An example graph created for the simple case of a Graph Transliterator that takes as
   input two token types, ``a`` and ``" "`` (space), and renders ``" "`` as ``" "``, and
   ``a`` as ``b`` unless it follows a token of class ``wb`` (for wordbreak), in which
   case it renders ``a`` as ``B``. The `rule` nodes are in double circles, and `token`
   nodes  are single circles. The numbers are the cost of the particular edge, and less
   costly edges are searched first. Previous token class (``prev_classes``) constraints
   are found on the edge before the leftmost leaf rule node.

To optimize the search, during initialization an :obj:`ordered_children` dictionary is
added to each non-leaf node. Its values are a list of node indexes sorted by cost
and keyed by the following `token`:

.. jupyter-execute::

  gt.graph.node[0]


Any `rule` connected to a node is added to each `ordered_children`. Any rule nodes
immediately following the current node are keyed to :obj:`__rules__`:

.. jupyter-execute::

  gt.graph.node[1]


Because of this preprocessing, Graph Transliterator does not need to iterate through all
of the outgoing edges of a node to find the next node to search.
