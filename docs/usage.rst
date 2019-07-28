.. py:module:: graphtransliterator

=====
Usage
=====

To use Graph Transliterator in a project::

    from graphtransliterator import GraphTransliterator

Overview
========
Graph Transliterator requires that you first configure
a :class:`GraphTransliterator`. Then you can transliterate an input string
using :meth:`GraphTransliterator.transliterate`. There are a few
additional methods that can be used to extract information for specific use
cases, such as details about which rules were matched.

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

Defining the rules for transliteration can be difficult, especially when
dealing with complex scripts. That is why Graph Transliterator uses an
"easy reading" format that allows you to enter the transliteration rules in
the popular `YAML <https://yaml.org/>`_ format, either from a string
(using :func:`GraphTransliterator.from_yaml`) or by reading from a file
or stream (:func:`GraphTransliterator.from_yaml_file`). You can also
initialize from the loaded contents of YAML
(:func:`GraphTransliterator.from_dict`).

Here is a quick sample that parameterizes :class:`GraphTransliterator` using an
easy reading YAML string (with comments):

>>> from graphtransliterator import GraphTransliterator
>>> yaml = """
...   tokens:
...     a: [vowel]               # type of token ("a") and its class (vowel)
...     bb: [consonant, b_class] # type of token ("bb") and its classes (consonant, b_class)
...     ' ': [wb]                # type of token (" ") and its class ("wb", for wordbreak)
...   rules:
...     a: A       # transliterate "a" to "A"
...     bb: B      # transliterate "bb" to "B"
...     a a: <2AS> # transliterate ("a", "a") to "<2AS>"
...     ' ': ' '   # transliterate ' ' to ' '
...   whitespace:
...     default: " "        # default whitespace token
...     consolidate: false  # whitespace should not be consolidated
...     token_class: wb     # whitespace token class
... """
>>> gt_one = GraphTransliterator.from_yaml(yaml)
>>> gt_one.transliterate('a')
'A'
>>> gt_one.transliterate('bb')
'B'
>>> gt_one.transliterate('aabb')
'<TWO_As>B'

The example above shows a very simple transliterator that replaces the
input token "a" with "A", "bb" with "B", " " with " ", and two "a" in a row
with "<2AS>". It does not consolidate whitespace, and treats " " as its
default whitespace token. Tokens contain strings of one or more characters.

Input Tokens and Token Class Settings
-------------------------------------
During transliteration, Graph Transliterator first attempts to convert the
input string into a list of tokens. This is done internally using
:meth:`GraphTransliterator.tokenize`:

  >>> gt_one.tokenize('abba')
  [' ', 'a', 'bb', 'a', ' ']

Note that the default whitespace  token is added to the start and end of the
input tokens.

Tokens can be more than one character, and longer tokens are matched first:

>>> yaml = """
...   tokens:
...     a: []      # "a" token with no classes
...     aa: []     # "aa" token with no classes
...     ' ': [wb]  # " " token and its class ("wb", for wordbreak)
...   rules:
...     aa: <DOUBLE_A>  # transliterate "aa" to "<DOUBLE_A>"
...     a: <SINGLE_A>   # transliterate "a" to "<SINGLE_A>"
...   whitespace:
...     default: " "        # default whitespace token
...     consolidate: false  # whitespace should not be consolidated
...     token_class: wb     # whitespace token class
... """
>>> gt_two = GraphTransliterator.from_yaml(yaml)
>>> gt_two.transliterate('a')
'<SINGLE_A>'
>>> gt_two.transliterate('aa')
'<DOUBLE_A>'
>>> gt_two.transliterate('aaa')
'<DOUBLE_A><SINGLE_A>'

Here the input "aaa" is transliterated as "<DOUBLE_A><SINGLE_A>", as the
longer token "aa" is matched before "a".

Tokens can be assigned zero or more classes. Each class is a string of your
choice. These classes are used in transliteration rules. In YAML they are
defined as a dictionary, but internally the rules are stored
as a dictionary of token strings keyed to a set of token classes. They can be
accessed using :attr:`GraphTransliterator.tokens`:

>>> gt_two.tokens
{'a': set(), 'aa': set(), ' ': {'wb'}}

Transliteration Rules
---------------------
Graph Transliterator can handle a variety of transliteration tasks.
To do so, it uses transliteration rules that contain **match settings** for
particular tokens in specific contexts and also a resulting **production**, or
string to be appended to the output string.

Match Settings
~~~~~~~~~~~~~~
Transliteration rules contain the following
parameters (ordered by where they would appear in a list of tokens):

  - **previous token classes** : a list of token classes (optional)
  - **previous tokens** : a list of tokens (optional)
  - **tokens** : a list of tokens
  - **next tokens** : a list of tokens (optional)
  - **next token classes** : a list of token classes (optional)

One or more (**tokens**) must be matched in a particular location. However,
specific tokens can be required before (**previous tokens**) or behind (**next
tokens**) those tokens. Additionally, particular token classes can be required
before (**previous token classes**) and behind (**next token classes**) all of
the specific tokens required (previous tokens, tokens, next tokens).

Depending on their complexity, these match conditions can be entered using the
"easy reading" format in the following ways.

If there are no required lookahead or lookbehind tokens, the rule can be as
follows:

.. code-block:: yaml

  rules:
     a a: aa  # two tokens (a,a), with production "production_aa"

If, in an addition to tokens, there are specific previous or following
tokens that must be matched, the rule can be entered as:

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

Token class names are indicated between angular brackets ("<classname>"). If
preceding and following tokens are not required but classes are, these can be
entered as follows:

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

If token classes must precede or follow specific tokens, these can be
entered as:

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

Graph Transliterator automatically orders the transliteration rules based on
the number of tokens required by the rule. It *picks the rule requiring the
longest match in a given context*. It does so by assigning a cost to each
transliteration rule that decreases depending on the number of tokens required
by the rule. More tokens decreases the cost of a rule causing it to be matched
first:

>>> yaml = """
...   tokens:
...     a: []
...     b: []
...     c: [class_of_c]
...     ' ': [wb]
...   rules:
...     a: <<A>>
...     a b: <<AB>>
...     b: <<B>>
...     c: <<C>>
...     ' ': _
...     <class_of_c> a b: <<AB_after_C>>
...   whitespace:
...     default: " "
...     consolidate: false
...     token_class: wb
... """
>>> gt_three = GraphTransliterator.from_yaml(yaml)
>>> gt_three.transliterate("ab")  # should match rule "a b"
'<<AB>>'
>>> gt_three.transliterate("cab") # should match rules: "c", and "<class_of_c> a b"
'<<C>><<AB_after_C>>'

Internally, Graph Transliterator uses a special :class:`TransliterationRule`
class. These can be accessed using :attr:`GraphTransliterator.rules`.
Rules are sorted by cost, lowest to highest:

>>> gt_three.rules
[TransliterationRule(production='<<AB_after_C>>', prev_classes=['class_of_c'], prev_tokens=None, tokens=['a', 'b'], next_tokens=None, next_classes=None, cost=0.22314355131420976), TransliterationRule(production='<<AB>>', prev_classes=None, prev_tokens=None, tokens=['a', 'b'], next_tokens=None, next_classes=None, cost=0.41503749927884376), TransliterationRule(production='<<A>>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562), TransliterationRule(production='<<B>>', prev_classes=None, prev_tokens=None, tokens=['b'], next_tokens=None, next_classes=None, cost=0.5849625007211562), TransliterationRule(production='<<C>>', prev_classes=None, prev_tokens=None, tokens=['c'], next_tokens=None, next_classes=None, cost=0.5849625007211562), TransliterationRule(production='_', prev_classes=None, prev_tokens=None, tokens=[' '], next_tokens=None, next_classes=None, cost=0.5849625007211562)]


Whitespace Settings
-------------------
Whitespace is often very important in transliteration tasks, as the form of
many letters may change at the start or end of words, as in the
right-to-left Perso-Arabic and left-to-right Indic scripts. Therefore, Graph
Transliterator requires the following **whitespace settings**:

- the **default** whitespace token
- the whitespace **token class**
- whether or not to **consolidate** whitespace

*A whitespace token and token class must be defined for any Graph
Transliterator*. A whitespace character is added temporarily to the start and
end of the input tokens during the transliteration process.

The ``consolidate`` option may be useful in particular transliteration tasks. It
replaces any sequential whitespace tokens in the input string with the default
whitespace character. At the start and end of input, it removes any whitespace:

>>> yaml = """
...   tokens:
...     a: []
...     ' ': [wb]
...   rules:
...     <wb> a: _A
...     a <wb>: A_
...     a: a
...     ' ': ' '
...   whitespace:
...     default: " "        # default whitespace token
...     consolidate: true   # whitespace should be consolidated
...     token_class: wb     # whitespace token class
... """
>>> gt = GraphTransliterator.from_yaml(yaml)
>>> gt.transliterate('a')   # whitespace present at start of string
'_A'
>>> gt.transliterate('aa')  # whitespace present at start and end of string
'_AA_'
>>> gt.transliterate(' a')  # consolidate removes whitespace at start of string
'_A'
>>> gt.transliterate('a ')  # consolidate removes whitespace at end of string
'_A'
>>> gt.transliterate('a')   # whitespace present at start of string


Whitespace settings are stored internally as a :class:`WhitespaceRules` and
can be accessed using :attr:`GraphTransliterator.whitespace`:

>>> gt.whitespace
WhitespaceRules(default=' ', token_class='wb', consolidate=False)

On Match Rules
--------------
Graph Transliterator allows the specification of strings to be inserted
before the productions of transliteration rules. These take as parameters:

- a list of **previous token classes**, preceding the location of the
  transliteration rule match
- a list of **next token classes**, from the index of the transliteration
  rule match
- a **production** string to insert

In the easy reading YAML format, the :obj:`onmatch_rules` are a list of
dictionaries. The key consists of the token class names in angular brackets
("<classname>"), and the previous classes to match are separated from the
following classes by a "+". The production is the value of the dictionary:

>>> yaml = """
...   tokens:
...     a: [vowel]
...     ' ': [wb]
...   rules:
...     a: A
...     ' ': ' '
...   whitespace:
...     default: " "
...     consolidate: false
...     token_class: wb
...   onmatch_rules:
...     - <vowel> + <vowel>: ',' # add a comma between vowels
...  """
>>> gt = GraphTransliterator.from_yaml(yaml)
>>> gt.transliterate('aa')
'A,A'

On Match rules are stored internally as a :class:`OnMatchRule` and can be
accessed using :attr:`GraphTransliterator.onmatch_rules`:

>>> gt.onmatch_rules
[OnMatchRule(prev_classes=['vowel'], next_classes=['vowel'], production=',')]


Metadata
--------
Graph Transliterator allows for the storage of metadata as another input
parameter, ``metadata``. It is a dictionary, and fields can be added to it:

>>> yaml = """
...   tokens:
...     a: []
...     ' ': [wb]
...   rules:
...     a: A
...     ' ': ' '
...   whitespace:
...     default: " "
...     consolidate: false
...     token_class: wb
...   metadata:
...     author: Author McAuthorson
...     version: 0.1.1
...     description: A sample Graph Transliterator
...   """
>>> gt = GraphTransliterator.from_yaml(yaml)
>>> gt.metadata
{'author': 'Author McAuthorson', 'version': '0.1.1', 'description': 'A sample Graph Transliterator'}

Unicode Support
---------------
Graph Transliterator allows Unicode characters to be specified by name,
including in YAML files, using the format "\\N{UNICODE CHARACTER NAME}" or
"\\u{####}" (where #### is the hexadecimal character code):

>>> yaml = """
...   tokens:
...     b: []
...     c: []
...     ' ': [wb]
...   rules:
...     b: \N{LATIN CAPITAL LETTER B}
...     c: \u0043    # hexadecimal Unicode character code for 'C'
...     ' ': ' '
...   whitespace:
...     default: " "
...     consolidate: false
...     token_class: wb
...   """
>>> gt = GraphTransliterator.from_yaml(yaml)
>>> gt.transliterate('b')
'B'
>>> gt.transliterate('c')
'C'

Configuring Directly
--------------------
In addition to using  :meth:`GraphTansliterator.from_yaml` and
:meth:`GraphTransliterator.from_yaml_file`, Graph Transliterator can
also be configured and initialized directly using basic Python types:

>>> settings = {
...   'tokens': {'a': ['vowel'],
...              ' ': ['wb']},
...   'rules': [
...       {'production': 'A', 'tokens': ['a']},
...       {'production': ' ', 'tokens': [' ']}],
...   'onmatch_rules': [
...       {'prev_classes': ['vowel'],
...        'next_classes': ['vowel'],
...        'production': ','}],
...   'whitespace': {
...       'default': ' ',
...       'consolidate': False,
...       'token_class': 'wb'},
...   'metadata': {
...       'author': 'Author McAuthorson'}
... }
>>> gt = GraphTransliterator(settings['tokens'], settings['rules'], settings['onmatch_rules'],
... settings['whitespace'], settings['metadata'])
>>> gt.transliterate('a')
'A'

This feature can be useful if generating a Graph Transliterator using code
as opposed to a configuration file.

Ambiguity Checking
------------------
Graph Transliterator, by default, will check for ambiguity in its
transliteration rules. If two rules of the same cost would match the same
string(s) and those strings would not be matched by a less costly rule,
an :exc:`AmbiguousTransliterationRulesException` occurs. Details of all
exceptions will be reported as a :meth:`logging.warning`:

>>> yaml_ = """
... tokens:
...   a: [class1, class2]
...   b: []
...   ' ': [wb]
... rules:
...   <class1> a: A
...   <class2> a: AA # ambiguous rule
...   <class1> b: BB
...   b <class2>: BB # also ambiguous
... whitespace:
...   default: ' '
...   consolidate: True
...   token_class: wb
... """
>>> gt = GraphTransliterator.from_yaml(yaml_)
WARNING:root:The pattern [{'a'}, {'a'}, {'b', 'a', ' '}] can be matched by both:
  <class1> a
  <class2> a
WARNING:root:The pattern [{'a'}, {'b'}, {'a'}] can be matched by both:
  <class1> b
  b <class2>
...
graphtransliterator.exceptions.AmbiguousTransliterationRulesException
>>>

The warning shows the set of possible previous tokens, matched tokens, and next
tokens as three sets.

Ambiguity checking is only necessary when using an untested Graph
Transliterator. It can be turned off during initialization. To do so,
set the initialization parameter :obj:`check_ambiguity` to `False`.

Ambiguity checking can also be done on demand using
:meth:`check_for_ambiguity`.

Setup Validation
----------------
Graph Transliterator validates both the "easy reading" configuration and the
direct configuration using the module :py:mod:`cerberus`. To turn off
validation, set the initialization parameter :obj:`check_settings` to
``False``. Setup errors will result in a :obj:`ValueError`, and errors will be
reported using :func:`logging.warning`.

Transliteration and Its Exceptions
==================================

The main method of Graph Transliterator is
:meth:`GraphTransliterator.transliterate`. It will return a string:

>>> GraphTransliterator.from_yaml(
... '''
... tokens:
...   a: []
...   ' ': [wb]
... rules:
...   a: A
...   ' ': '_'
... whitespace:
...   default: ' '
...   consolidate: True
...   token_class: wb
... ''').transliterate("a a")
'A_A'

Details of transliteration error exceptions will be logged using
:meth:`logging.warning`.

Unrecognizable Input Token
--------------------------

Unless the :class:`GraphTransliterator` is initialized with or has the property
:obj:`ignore_errors` set as :obj:`True`,
:meth:`GraphTransliterator.transliterate` will raise
:exc:`UnrecognizableInputTokenException` when character(s) in the input string
do not correspond to any defined types of input tokens. In both cases, there
will be a :meth:`logging.warning`:

>>> from graphtransliterator import GraphTransliterator
>>> yaml_ = """
...   tokens:
...    a: []
...    ' ': [wb]
...   rules:
...     a: A
...     ' ': ' '
...   whitespace:
...     default: " "
...     consolidate: true
...     token_class: wb
... """
>>> GraphTransliterator.from_yaml(yaml_).transliterate("a!a") # ignore_errors=False
Unrecognizable token ! at pos 1 of a!a
  ...
graphtransliterator.exceptions.UnrecognizableInputTokenException
>>> GraphTransliterator.from_yaml(yaml_, ignore_errors=True).transliterate("a!a") # ignore_errors=True
Unrecognizable token ! at pos 1 of a!a
'AA'

No Matching Transliteration Rule
--------------------------------

Another possible error occurs when no transliteration rule can be identified
at a particular index in the index string. In that case, there will be a
:meth:`logging.warning`. If the parameter :obj:`ignore_errors` is set to
:obj:`True`, the token index will be advanced. Otherwise, there will be a
:exc:`NoMatchingTransliterationRuleException`:

>>> yaml_='''
...   tokens:
...     a: []
...     b: []
...     ' ': [wb]
...   rules:
...     a: A
...     b (a): B
...   whitespace:
...     default: ' '
...     token_class: wb
...     consolidate: False
... '''
>>> gt = GraphTransliterator.from_yaml(yaml_)
>>> gt.transliterate("ab")
No matching transliteration rule at token pos 2 of [' ', 'a', 'b', ' ']
  ...
graphtransliterator.exceptions.NoMatchingTransliterationRuleException
>>> gt.ignore_errors = True
>>> gt.transliterate("ab")
No matching transliteration rule at token pos 2 of [' ', 'a', 'b', ' ']
'A'

Additional Methods
==================

Graph Transliterator also offers a few additional methods that may be
useful for particular tasks.

Serialization
-------------

The settings of a Graph Transliterator can be serialized using
:meth:`serialize`. It returns all of the settings of an initialized Graph
Transliterator as a dictionary.

Matching at an Index
--------------------

The method :meth:`match_at` is also public. It matches
the best transliteration rule at a particular index, which is the rule that
contains the largest number of required tokens. The method also has the
option :obj:`match_all` which, if set, returns all possible transliteration
matches at a particular location:

>>> gt = GraphTransliterator.from_yaml('''
...         tokens:
...             a: []
...             a a: []
...             ' ': [wb]
...         rules:
...             a: <A>
...             a a: <AA>
...         whitespace:
...             default: ' '
...             consolidate: True
...             token_class: wb
... ''')
>>> tokens = gt.tokenize("aa")
>>> tokens # whitespace added to ends
[' ', 'a', 'a', ' ']
>>> gt.match_at(1, tokens) # returns index to rule
0
>>> gt.rules[gt.match_at(1, tokens)] # actual rule
TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.41503749927884376)
>>> gt.match_at(1, tokens, match_all=True) # index to rules, with match_all
[0, 1]
>>>
>>> [gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)] # actual rules, with match_all
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.41503749927884376), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562)]

Details of Matches
------------------

Each Graph Transliterator has a property :attr:`last_matched_rules` which
returns a list of :obj:`TransliterationRule` of the previously matched
transliteration rules:

>>> gt.transliterate("aaa")
'<AA><A>'
>>> gt.last_matched_rules
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.41503749927884376), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562)]

The particular tokens matched by those rules can be accessed using
:attr:`last_matched_rule_tokens`:

>>> gt.last_matched_rule_tokens
[['a', 'a'], ['a']]

Pruning of Rules
----------------

In particular cases, it may be useful to remove certain transliteration rules
from a more robustly defined Graph Transliterator based on the string output
produced by the rules. That can be done using :meth:`pruned_of`:

>>> gt.rules
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.41503749927884376), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562)]
>>> gt.pruned_of('<AA>').rules
[TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562)]
>>> gt.pruned_of(['<A>', '<AA>']).rules


Internal Graph
==============
Graph Transliterator creates a directed tree during its initialization. During
calls to :meth:`transliterate`, it searches that graph to find the best
transliteration match at a particular index in the tokens of the input string.

DirectedGraph
-------------

The tree is an instance of :class:`DirectedGraph` that can be accessed using
:attr:`GraphTransliterator.graph`. It contains: a list of nodes, each
consisting of a dictionary of attributes; a dictionary of edges keyed between
the head and tail of an edge that contains a dictionary of edge attributes;
and finally an edge list.

>>> gt = GraphTransliterator.from_yaml(
...     """
...     tokens:
...       a: []
...       ' ': [wb]
...     rules:
...       a: b
...       <wb> a: B
...       ' ': ' '
...     whitespace:
...       token_class: wb
...       default: ' '
...       consolidate: false
...     """)
>>> gt.graph
<graphtransliterator.graphs.DirectedGraph object at 0x101d0be48>

Nodes
-----

The tree has nodes of three types: `Start`, `token`, and `rule`. A single
`Start` node, the root, is connected to all other nodes. A `token` node
corresponds to a token having been matched. Finally, `rule` nodes are leaf
nodes (with no outgoing edges) that correspond to matched transliteration rules:

>>> gt.graph.node
[{'type': 'Start', 'ordered_children': {'a': [1], ' ': [4]}}, {'type': 'token', 'token': 'a', 'ordered_children': {'__rules__': [2, 3]}}, {'type': 'rule', 'rule_key': 0, 'rule': TransliterationRule(production='B', prev_classes=['wb'], prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.41503749927884376), 'accepting': True, 'ordered_children': {}}, {'type': 'rule', 'rule_key': 1, 'rule': TransliterationRule(production='b', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562), 'accepting': True, 'ordered_children': {}}, {'type': 'token', 'token': ' ', 'ordered_children': {'__rules__': [5]}}, {'type': 'rule', 'rule_key': 2, 'rule': TransliterationRule(production=' ', prev_classes=None, prev_tokens=None, tokens=[' '], next_tokens=None, next_classes=None, cost=0.5849625007211562), 'accepting': True, 'ordered_children': {}}]

Edges
-----

Edges between these nodes may have different constraints in their
attributes:

>>> gt.graph.edge
{0: {1: {'token': 'a', 'cost': 0.41503749927884376}, 4: {'token': ' ', 'cost': 0.5849625007211562}}, 1: {2: {'cost': 0.41503749927884376, 'constraints': {'prev_classes': ['wb']}}, 3: {'cost': 0.5849625007211562}}, 4: {5: {'cost': 0.5849625007211562}}}

Before the `token` nodes, there is a `token` constraint on the edge
that must be matched before the transliterator can visit the token node:

>>> gt.graph.edge[0][1]
{'token': 'a', 'cost': 0.41503749927884376}

On the edges before rules there may be other `constraints`, such as certain tokens
preceding or following tokens of the corresponding transliteration rule:

>>> gt.graph.edge[1][2]
{'cost': 0.41503749927884376, 'constraints': {'prev_classes': ['wb']}}

An edge list is also maintained that consists of a tuple of (head, tail):

>>> gt.graph.edge_list
[(0, 1), (1, 2), (1, 3), (0, 4), (4, 5)]

Search and Preprocessing
------------------------

Graph Transliterator uses a best-first search, implemented using a stack,
that finds the transliteration with the the lowest cost. The cost function is:

.. math::

   \text{cost}(rule) = \log_2{\big(1+\frac{1}{1+\text{count_of_tokens_in}(rule)}\big)}

It results in a number between 1 and 0 that lessens as more tokens
must be matched. Each edge on the graph has a cost attribute
that is set to the lowest cost transliteration rule following it.
When transliterating, Graph Transliterator will try lower cost edges first and
will backtrack if the constraint conditions are not met.

.. _sample_graph:
.. figure:: figure1.png
   :alt: Sample graph

   An example graph created for the simple case of a Graph Transliterator
   that takes as input two token types, ``a`` and ``" "`` (space), and
   renders ``" "`` as ``" "``, and ``a`` as ``b`` unless it follows a token
   of class ``wb`` (for wordbreak), in which case it renders ``a`` as ``B``.
   The `rule` nodes are in double circles, and `token` nodes  are single
   circles. The numbers are the cost of the particular edge, and less costly
   edges are searched first. Previous token class (``prev_classes``)
   constraints are found on the edge before the leftmost leaf rule
   node.

To optimize the search, during initialization an :obj:`ordered_children`
dictionary is added to each non-leaf node. Its values are a sorted list of
node indexes sorted by cost and keyed by the following `token`:

>>> gt.graph.node[0]
{'type': 'Start', 'ordered_children': {'a': [1], ' ': [4]}}

Any `rule` connected to a node is added to each `ordered_children`. Any rule
nodes immediately following the current node are keyed to :obj:`__rules__`:

>>> gt.graph.node[1]
{'type': 'token', 'token': 'a', 'ordered_children': {'__rules__': [2, 3]}}

Because of this preprocessing, Graph Transliterator does not need to iterate
through all of the outgoing edges of a node to find the next node to search.
