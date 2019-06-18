.. py:module:: graphtransliterator

=====
Usage
=====

To use Graph Transliterator in a project::

    from graphtransliterator import GraphTransliterator

Overview
========
Graph Transliterator requires that you must first configure
a :class:`GraphTransliterator`. Then you can transliterate an input string
using :meth:`GraphTransliterator.transliterate`. There are a few
additional methods that can be used to extract additional information.

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
dealing with complex scripts. That is why Graph Transliterator permits an
"easy reading" format that allows you to enter the transliteration rules in
the popular `YAML <https://yaml.org/>`_ format, either directly in a string
(using :func:`GraphTransliterator.from_yaml`) or by reading from a file
or stream (:func:`GraphTransliterator.from_yaml_file`). The loaded contents of
the YAML can also be loaded from a dictionary
(:func:`GraphTransliterator.from_yaml_file`).

Here is a quick sample that parameterizes :class:`GraphTransliterator` using an
easy reading YAML string:

>>> from graphtransliterator import GraphTransliterator
>>> yaml = """
...   tokens:
...     a: [vowel]               # type of token ("a") and its class (vowel)
...     bb: [consonant, b_class] # definition of type of token ("a") and its classes
...     ' ': [wb]                # type of token (" ") and its class ("wb", for wordbreak)
...   rules:
...     a: A       # transliterate "a" to "A"
...     bb: B      # transliterate "bb" to "B"
...     a a: <2AS> # transliterate ("a", "a") to "2AS"
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
:meth:`GraphTransliterator.tokenize`.

Here is an example using transliterator defined above:

  >>> gt_one.tokenize('abba')
  [' ', 'a', 'bb', 'a', ' ']

Note that the default whitespace is added to the start and end of the input
tokens.

Tokens can be more than one character, and longer tokens are matched first:

>>> yaml = """
...   tokens:
...     a: []     # "a" token with no classes
...     aa: []    # "aa" token with no classses
...     ' ': [wb] # " " token and its class ("wb", for wordbreak)
...   rules:           # transliteration rules
...     aa: <DOUBLE_A>   # transliterate "aa" to "DOUBLE_A"
...     a: <SINGLE_A>    # transliterate "b" to "B"
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
defined as a dictionary, but internally rules are stored
as a dictionary of token strings keyed to a set of token classes. They can be
accessed using the  :func:`GraphTransliterator.tokens`:

>>> gt_two.tokens
{'a': set(), 'aa': set(), ' ': {'wb'}}

Transliteration Rules
---------------------
Graph Transliterator can handle a substantial number of transliteration tasks.
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

If there are no required additional tokens, the rule can be entered as:

.. code-block:: yaml

  rules:
     a a: aa  # two tokens (a,a), with production "production_aa"

If, in an addition to tokens, there are specific previous or following
tokens that mut be matched, the rule can be entered as:

.. code-block:: yaml

  tokens:
    a: []
    b: []
    c: []
    d: []
  rules:
     a (b): a_before_b  # matches  token 'a' with the next token 'b'
     (c) a: a_after_c   # matches token 'a' when the previous token is 'b'
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
    c <class_b>: c_after _class_b # match token 'c' before a token of class 'class_b`
    <class_b> a: a_before_class_b # match token 'a' before a token of class `class_b`
    <class_b> a <class_b>: a_between_class_b # match token 'a' between tokens of class_b

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
    (<class_c> d) a (b <class_c> <class_d>): x # match 'a' after token of 'class_c' and before 'd' and a token of 'class_c' and of 'class_d'
  whitespace:
    default: ' '
    token_class: wb
    consolidate: false

By design, Graph Transliterator *picks the most specific rule in a a given
context*. It does so by assigning a cost to each transliteration rule, and
picks the least costly one. The cost is determined by the total number
of tokens required by the rule. More tokens decreases the cost of a rule
causing it to be matched first:

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
[TransliterationRule(production='<<AB_after_C>>', prev_classes=['class_of_c'], prev_tokens=None, tokens=['a', 'b'], next_tokens=None, next_classes=None, cost=0.22314355131420976), TransliterationRule(production='<<AB>>', prev_classes=None, prev_tokens=None, tokens=['a', 'b'], next_tokens=None, next_classes=None, cost=0.28768207245178085), TransliterationRule(production='<<A>>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.4054651081081644), TransliterationRule(production='<<B>>', prev_classes=None, prev_tokens=None, tokens=['b'], next_tokens=None, next_classes=None, cost=0.4054651081081644), TransliterationRule(production='<<C>>', prev_classes=None, prev_tokens=None, tokens=['c'], next_tokens=None, next_classes=None, cost=0.4054651081081644), TransliterationRule(production='_', prev_classes=None, prev_tokens=None, tokens=[' '], next_tokens=None, next_classes=None, cost=0.4054651081081644)]


Whitespace Settings
-------------------
Whitespace is often very important in transliteration tasks, as the form of
many letters may change at the start or end of words, as in the
right-to-left Arabic and left-to-right Indic scripts. Therefore, Graph
Transliterator requires the following **whitespace settings**:

- the **default** whitespace token
- the whitespace **token class**
- whether or not to **consolidate** whitespace

*A whitespace token and token class must be defined for any Graph
Transliterator*. A whitespace character is added temporarily to the start and
end of the input tokens during the transliteration process.

The ``consolidate`` option may be useful in particular transliteration tasks. It
replace any sequential whitespace tokens in the input string with the default
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
>>> gt.transliterate('a') # whitespace present at start of string
'_A'
>>> gt.transliterate('aa') # whitespace present at start and end of string
'_AA_'
>>> gt.transliterate(' a') # conslidate removes whitespace at start of string
'_A'
>>> gt.transliterate('a ') # consolidate removes whitespace at end of string
'_A'
>>> gt.transliterate('a') # whitespace present at start of string


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

In the easy reading YAML format, the :obj:``onmatch_rules`` are a list of
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
parameters. That is a dictionary, and fields can be added to it:

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
...     c: \u0043
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

>>> yaml = """
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
>>> gt = GraphTransliterator.from_yaml(yaml)
WARNING:root:The pattern [{'a'}]+[{'a'}] can be matched by both:
  ['class1'] a
  ['class2'] a
WARNING:root:The pattern [{'a'}]+[{'b'}, {'a'}] can be matched by both:
  ['class1'] b
  b class2
Traceback (most recent call last):
  ...
graphtransliterator.exceptions.AmbiguousTransliterationRulesException

Note that in the latter case 'b' following a token of 'class1' and 'b'
preceding a token of 'class2' are ambiguous as both rules would be of
the same cost. The warning shows the possible previous tokens before the
possible matched tokens of the transliteration rule as two lists.

Ambiguity checking is only necessary when using an untested Graph
Transliterator. It can be turned off during initialization. To do so,
set the initialization parameter :obj:`check_ambiguity` to `False`. It can
also be done on demand using the :meth:`check_for_ambiguity`.

Setup Validation
----------------
Graph Transliterator validates both the "easy reading" configuration and the
direct configuration using the module :py:mod:`cerberus`. To turn off
validation, set the initialization parameter :obj:`check_settings` to `False`.
Setup errors will result in a :obj:`ValueError`, and errors will be reported
using :func:`logging.warning`.

Transliteration and Its Exceptions
==================================

The main method of Graph Transliterator is
:meth:`GraphTransliterator.transliterate`. Transliteration error exceptions
will be logged using :meth:`logging.warning`.

Unrecognizable Input Token
~~~~~~~~~~~~~~~~~~~~~~~~~

If the :class:`GraphTransliterator` is initialized with or has the property
:obj:`ignore_errors` set as :obj:`True`, no exceptions will be raised, and the token
will be skipped. Otherwise, the :meth:`GraphTransliterator.transliterate` may
raise :exc:`UnrecognizableInputTokenException` when character(s) in the input
string do not correspond to any defined types of input tokens:

>>> GraphTransliterator.from_yaml("""
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
... """).transliterate("a!a") # contains unknown token !
Unrecognizable token ! at pos 1 of a!a
Traceback (most recent call last):
  ...
graphtransliterator.exceptions.UnrecognizableInputTokenException
>>> GraphTransliterator.from_yaml("""
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
... """, ignore_errors=True).transliterate("a!a")
Unrecognizable token ! at pos 1 of a!a
Unrecognizable token a at pos 2 of a!a
'A'

No Matching Transliteration Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another possible error occurs when no transliteration rule can be identified
at a particular index in the index strings. In that case, there will be a
:meth:`logging.warning`. If the parameter :obj:`ignore_errors` is set to
:obj:`True`, the token index will be advanced. Otherwise, there will be a
:exc:`NoMatchingTransliteratuRuleException`:

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
...     consolidate: false
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
~~~~~~~~~~~~~

The settings of a Graph Transliterator can be serialized using
:meth:`serialize.` It returns all of the settings of the Graph Transliterator
as a dictionary.

Matching at an Index
~~~~~~~~~~~~~~~~~~~~

The method :meth:`match_at` is also public. It matches
the best transliteratio at a particular index. It also has the
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
TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.28768207245178085)
>>> gt.match_at(1, tokens, match_all=True) # index to rules, with match_all
[0, 1]
>>>
>>> [gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)] # actual rules, with match_all
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.28768207245178085), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.4054651081081644)]
>>>

Details of Matches
~~~~~~~~~~~~~~~~~~
Each Graph Transliterator has a property :attr:`last_matched_rules` which
returns as a list of the :obj:`TransliterationRule` the previously matched
transliteration rules:

>>> gt.transliterate("aaa")
'<AA><A>'
>>> gt.last_matched_rules
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.28768207245178085), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.4054651081081644)]

The particular tokens matched by those rules can be accessed using :attr:`last_matched_rule_tokens`:

>>> gt.last_matched_rule_tokens
[['a', 'a'], ['a']]

Pruning of Rules
~~~~~~~~~~~~~~~~
In particular cases, it may be useful to remove certain transliteration rules
from a more robustly defined Graph Transliterator based on the string output
produced by of the rules. That can be done using :meth:`pruned_of`:

>>> gt.rules
[TransliterationRule(production='<AA>', prev_classes=None, prev_tokens=None, tokens=['a', 'a'], next_tokens=None, next_classes=None, cost=0.28768207245178085), TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.4054651081081644)]
>>> gt.pruned_of('<AA>').rules
[TransliterationRule(production='<A>', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.4054651081081644)]
>>> gt.pruned_of(['<A>', '<AA>']).rules


Internal Graph
==============
Graph Transliterator creates a directed tree during its initialization. During
calls to :meth:`transliterate`, it searches that graph to find the best
transliteration match at a particular index in the tokens of the input string.

The tree is an instance of :class:`DirectedGraph` that can be accessed using
the :meth:`GraphTransliterator.graph`. It contains: a list of nodes, each
consisting of a dictionary of attributes; a dictionary of edges keyed between
the head and tail of an edge that contains a dictionary of edge attributes;
and finally an edge list consisting of a tuple of (head, tail).

The tree has nodes of three types: start, token, and rule. A single "start"
node, the root, is connected to all other nodes. "Token" nodes correspond to a
token having been matched. Final "rule"-type nodes are leaf nodes (with
no outgoing edges) correspond to transliteration rules.

Edges between these nodes may have different constraints in their
attributes. Before the "token" nodes, there is a "token" constraint on the edge
that must be matched before the transliterator can visit the token node. On the
edges before rules there may be other "constraints," such as certain tokens
preceding or following tokens of the corresponding transliteration rule.

Graph Transliterator uses a best-first search, implemented using a stack,
that finds the transliteration with the the lowest cost. The cost function is:

:math:`\log{\big(1+\frac{1}{1+\text{count of tokens required by
rule}}\big)}`

It results in a number roughly between .7 and 0 that lessens as more tokens
must be matched. Each edge on the graph has a cost attribute
that is set to the lowest cost transliteration rule following it.
When transliterating, Graph Transliterator will try lower cost edges first and
will backtrack if the constraint conditions are not met.

.. _sample_graph:
.. figure:: figure1.png
   :alt: Sample graph

   Sample graph created for Graph Transliterator that  renders "a" after
   whitespace (a token of the class "<wb>" for wordbreak) as "B", "a" as "b",
   and " " as " ". Rule nodes are in double circles, whereas token nodes are
   single circles. The numbers are the cost of the particular edge, and less
   costly edges are tried first. Previous token class (`prev_classes`)
   constraints are in a dictionary on the edge before the leaf rule node.

To optimize the search, during initialization an :obj:`ordered_children`
dictionary is added to each non-leaf node. Its values are a sorted list of
node indexes. Any rule nodes following the current node are keyed to
:obj:`__rules__`. Any following token nodes are keyed by their next token, sorted by
cost, and also contain the node's rule nodes. Because of this
preprocessing, Graph  Transliterator does not need to iterate through all of
the outgoing edges of a node to find the next node to search.
