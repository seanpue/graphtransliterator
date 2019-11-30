# -*- coding: utf-8 -*-

"""
GraphTransliterator core classes.
"""
from graphtransliterator import __version__ as __version__
import itertools
import json
import logging

# import pkg_resources
import re
import unicodedata
import yaml
from .exceptions import (
    AmbiguousTransliterationRulesException,
    IncompleteOnMatchRulesCoverageException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)
from .initialize import (
    _graph_from,
    _onmatch_rules_lookup,
    _tokenizer_pattern_from,
    _tokens_by_class_of,
)
from .process import _process_easyreading_settings
from .schemas import (
    DirectedGraphSchema,
    EasyReadingSettingsSchema,
    OnMatchRuleSchema,
    SettingsSchema,
    TransliterationRuleSchema,
    WhitespaceSettingsSchema,
)
from collections import deque
from .graphs import VisitLoggingDirectedGraph, VisitLoggingList
from marshmallow import fields, post_load, Schema, validates_schema, ValidationError

logger = logging.getLogger("graphtransliterator")


class GraphTransliteratorSchema(Schema):
    """Schema for Graph Transliterator."""

    tokens = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.Str()), required=True
    )
    rules = fields.Nested(TransliterationRuleSchema, many=True, required=True)

    whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
    onmatch_rules = fields.Nested(
        OnMatchRuleSchema, many=True, required=False, allow_none=True
    )

    metadata = fields.Dict(
        keys=fields.Str(), required=False  # No restriction on values
    )
    ignore_errors = fields.Bool(required=False)
    onmatch_rules_lookup = fields.Dict(required=False, allow_none=True)
    tokens_by_class = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.Str), required=False
    )
    graph = fields.Nested(DirectedGraphSchema, required=False)
    tokenizer_pattern = fields.Str(required=False)
    graphtransliterator_version = fields.Str(required=False)
    check_ambiguity = fields.Bool(required=False)
    # field for coverage
    coverage = fields.Bool(required=False)

    class Meta:
        ordered = True

    @post_load
    def make_GraphTransliterator(self, data, **kwargs):
        # Convert lists to sets
        for key in ("tokens", "tokens_by_class"):
            if data.get(key):  # tokens_by_class can be generated
                data[key] = {k: set(v) for k, v in data[key].items()}
        # Do not check ambiguity if deserializing serialized GraphTransliterator
        data["check_ambiguity"] = False
        if data.get("coverage"):
            return CoverageTransliterator(**data)
        return GraphTransliterator(**data)

    @validates_schema
    def validate_onmatch_rules_lookup(self, data, **kwargs):
        """Check that if there are onmatch_rules_lookup there are onmatch_rules."""
        if data.get("onmatch_rules_lookup") and not data.get("onmatch_rules"):
            raise ValidationError(
                "Contains onmatch_rules_lookup but not onmatch_rules."
            )


class GraphTransliterator:
    """
    A graph-based transliteration tool that lets you convert the symbols
    of one language or script to those of another using rules that you define.

    Transliteration of tokens of an input string to an output string is
    configured by: a set of input token types with classes, pattern-matching rules
    involving sequences of tokens as well as preceding or following tokens and
    token classes, insertion rules between matches, and optional consolidation
    of whitespace. Rules are ordered by specificity.

    Note
    ----
    This constructor does not validate settings and should typically not be called
    directly. Use :meth:`from_dict` instead. For "easy reading" support, use
    :meth:`from_easyreading_dict`, :meth:`from_yaml`, or :meth:`from_yaml_file`.
    Keyword parameters used here (``ignore_errors``, ``check_ambiguity``) can be passed
    from those other constructors.

    Parameters
    ----------
    tokens : `dict` of {`str`: `set` of `str`}
        Mapping of input token types to token classes

    rules : `list` of `TransliterationRule`
        `list` of transliteration rules ordered by cost

    onmatch_rules : `list` of :class:`OnMatchRule`, or `None`
        Rules for output to be inserted between tokens
        of certain classes when a transliteration rule has been matched
        but before its production string has been added to the output

    whitespace: `WhitespaceRules`
        Rules for handling whitespace

    metadata: `dict` or `None`
        Metadata settings

    ignore_errors: `bool`, optional
        If true, transliteration errors are ignored and do not raise an
        exception. The default is false.

    check_ambiguity: `bool`, optional
        If true (default), transliteration rules are checked for ambiguity. :meth:`load()`
        and :meth:`loads` do not check ambiguity by default.

    onmatch_rules_lookup: `dict` of {`str`: dict of {`str`: `list` of `int`}}, optional`
        OnMatchRules lookup, used internally, will be generated if not present.

    tokens_by_class: `dict` of {`str`: `set` of `str`}, optional
        Tokens by class, used internally, will be generated if not present.

    graph: `DirectedGraph`, optional
        Directed graph used by Graph Transliterator, will be generated if not present.

    tokenizer_pattern: `str`, optional
        Regular expression pattern for input string tokenization, will be generated if
        not present.

    graphtransliterator_version: `str`, optional
        Version of graphtransliterator, added by `dump()` and `dumps()`.

    coverage: `bool`, optional
        Create CoverageTransliterator, which tracks node, edge, and onmatch rule access

    Example
    -------
    .. jupyter-execute::


      from graphtransliterator import GraphTransliterator, OnMatchRule, TransliterationRule, WhitespaceRules
      settings = {'tokens': {'a': {'vowel'}, ' ': {'wb'}}, 'onmatch_rules': [OnMatchRule(prev_classes=['vowel'], next_classes=['vowel'], production=',')], 'rules': [TransliterationRule(production='A', prev_classes=None, prev_tokens=None, tokens=['a'], next_tokens=None, next_classes=None, cost=0.5849625007211562), TransliterationRule(production=' ', prev_classes=None, prev_tokens=None, tokens=[' '], next_tokens=None, next_classes=None, cost=0.5849625007211562)], 'metadata': {'author': 'Author McAuthorson'}, 'whitespace': WhitespaceRules(default=' ', token_class='wb', consolidate=False)}
      gt = GraphTransliterator(**settings)
      gt.transliterate('a')


    See Also
    --------
    from_dict : Constructor from dictionary of settings
    from_easyreading_dict : Constructor from  dictionary in "easy reading" format
    from_yaml : Constructor from YAML string in "easy reading" format
    from_yaml_file : Constructor from YAML file in "easy reading" format
"""  # noqa

    def __init__(
        self,
        tokens,
        rules,
        whitespace,
        onmatch_rules=None,
        metadata=None,
        ignore_errors=False,
        check_ambiguity=True,
        onmatch_rules_lookup=None,
        tokens_by_class=None,
        graph=None,
        tokenizer_pattern=None,
        graphtransliterator_version=None,
        coverage=False,
    ):
        self._tokens = tokens
        self._rules = rules
        self._tokens_by_class = tokens_by_class or _tokens_by_class_of(tokens)
        self._check_ambiguity = check_ambiguity
        if check_ambiguity:
            check_for_ambiguity(self)
        self._whitespace = whitespace

        if onmatch_rules:
            self._onmatch_rules = onmatch_rules
            if onmatch_rules_lookup:
                self._onmatch_rules_lookup = onmatch_rules_lookup
            else:
                self._onmatch_rules_lookup = _onmatch_rules_lookup(
                    tokens, onmatch_rules
                )
        else:
            self._onmatch_rules = None
            self._onmatch_rules_lookup = None

        self._metadata = metadata
        self._ignore_errors = ignore_errors

        if not tokenizer_pattern:
            tokenizer_pattern = _tokenizer_pattern_from(list(tokens.keys()))
        self._tokenizer_pattern = tokenizer_pattern
        self._tokenizer = re.compile(tokenizer_pattern, re.S)

        if not graph:
            graph = _graph_from(rules)
        self._graph = graph

        self._rule_keys = []  # last matched rules

        # When, or if, necessary, add version checking here
        if not graphtransliterator_version:
            graphtransliterator_version = __version__
        # problems with readthedocs + jupyter-sphinx due to pythonpath import
        # pkg_resources.require("graphtransliterator")[0].version
        self._graphtransliterator_version = graphtransliterator_version

    def _match_constraints(self, target_edge, curr_node, token_i, tokens):
        """
        Match edge constraints.

        Called on edge before a rule. `token_i` is set to location right
        after tokens consumed.

        """
        constraints = target_edge.get("constraints")
        if not constraints:
            return True
        for c_type, c_value in constraints.items():
            if c_type == "prev_tokens":
                num_tokens = len(curr_node["rule"].tokens)
                # presume for rule (a) a, with input "aa"
                # ' ', a, a, ' '  start (token_i=3)
                #             ^
                #         ^       -1 subtract num_tokens
                #      ^          - len(c_value)
                start_at = token_i
                start_at -= num_tokens
                start_at -= len(c_value)

                if not self._match_tokens(
                    start_at,
                    c_value,
                    tokens,
                    check_prev=True,
                    check_next=False,
                    by_class=False,
                ):
                    return False
            elif c_type == "next_tokens":
                # presume for rule a (a), with input "aa"
                # ' ', a, a, ' '  start (token_i=2)
                #         ^
                start_at = token_i

                if not self._match_tokens(
                    start_at,
                    c_value,
                    tokens,
                    check_prev=False,
                    check_next=True,
                    by_class=False,
                ):
                    return False

            elif c_type == "prev_classes":
                num_tokens = len(curr_node["rule"].tokens)
                # presume for rule (a <class_a>) a, with input "aaa"
                # ' ', a, a, a, ' '
                #                ^     start (token_i=4)
                #            ^         -num_tokens
                #         ^            -len(prev_tokens)
                #  ^                   -len(prev_classes)
                start_at = token_i
                start_at -= num_tokens
                prev_tokens = constraints.get("prev_tokens")
                if prev_tokens:
                    start_at -= len(prev_tokens)
                start_at -= len(c_value)
                if not self._match_tokens(
                    start_at,
                    c_value,
                    tokens,
                    check_prev=True,
                    check_next=False,
                    by_class=True,
                ):
                    return False

            elif c_type == "next_classes":
                # presume for rule a (a <class_a>), with input "aaa"
                # ' ', a, a, a, ' '
                #         ^          start (token_i=2)
                #            ^       + len of next_tokens (a)
                start_at = token_i
                next_tokens = constraints.get("next_tokens")
                if next_tokens:
                    start_at += len(next_tokens)
                if not self._match_tokens(
                    start_at,
                    c_value,
                    tokens,
                    check_prev=False,
                    check_next=True,
                    by_class=True,
                ):
                    return False

        return True

    def match_at(self, token_i, tokens, match_all=False):
        """
        Match best (least costly) transliteration rule at a given index in the
        input tokens and return the index to  that rule. Optionally, return all
        rules that match.

        Parameters
        ----------
        token_i : `int`
            Location in `tokens` at which to begin
        tokens : `list` of `str`
            List of tokens
        match_all : `bool`, optional
            If true, return the index of all rules matching at the given
            index. The default is false.

        Returns
        -------
        `int`, `None`, or `list` of `int`
            Index of matching transliteration rule in
            :attr:`GraphTransliterator.rules` or None. Returns a `list` of
            `int` or an empty `list` if ``match_all`` is true.

        Note
        ----
        Expects whitespaces token at beginning and end of `tokens`.

        Examples
        --------

        .. jupyter-execute::

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

          [gt.rules[_] for _ in gt.match_at(1, tokens, match_all=True)]

        """  # noqa

        graph = self._graph
        graph_node = graph.node
        graph_edge = graph.edge
        if match_all:
            matches = []
        stack = deque()

        def _append_children(node_key, token_i):
            children = None
            ordered_children = graph_node[node_key].get("ordered_children")
            if ordered_children:
                children = ordered_children.get(tokens[token_i])
                if children:
                    # reordered high to low for stack:
                    for child_key in reversed(children):

                        stack.appendleft((child_key, node_key, token_i))
                else:
                    rules_keys = ordered_children.get("__rules__")  # leafs
                    if rules_keys:
                        # There may be more than one rule, as certain rules have
                        # constraints on them.
                        # Reordered so higher cost go on stack last.
                        for rule_key in reversed(rules_keys):
                            stack.appendleft((rule_key, node_key, token_i))

        _append_children(0, token_i)  # Append all children of root node

        while stack:  # LIFO
            node_key, parent_key, token_i = stack.popleft()
            assert token_i < len(tokens), "way past boundary"

            curr_node = graph_node[node_key]
            # Constraints are only on preceding edge if it is accepting
            # But edge is accessed regardless to test coverage
            incident_edge = graph_edge[parent_key][node_key]
            # Pass edge, curr_node, token index, and tokens to check constraints
            if curr_node.get("accepting") and self._match_constraints(
                incident_edge, curr_node, token_i, tokens
            ):
                if match_all:
                    matches.append(curr_node["rule_key"])
                    continue
                else:
                    return curr_node["rule_key"]
            else:
                if token_i < len(tokens) - 1:
                    token_i += 1
                _append_children(node_key, token_i)
        if match_all:
            return matches

    def _match_tokens(
        self, start_i, c_value, tokens, check_prev=True, check_next=True, by_class=False
    ):
        """Match tokens, with boundary checks."""

        if check_prev and start_i < 0:
            return False
        if check_next and start_i + len(c_value) > len(tokens):
            return False
        for i in range(0, len(c_value)):
            if by_class:
                if not c_value[i] in self._tokens[tokens[start_i + i]]:
                    return False
            elif tokens[start_i + i] != c_value[i]:
                return False
        return True

    @property
    def graph(self):
        """`DirectedGraph`: Graph used in transliteration."""
        return self._graph

    @property
    def graphtransliterator_version(self):
        """`str`: Graph Transliterator version"""
        return self._graphtransliterator_version

    @property
    def ignore_errors(self):
        """`bool`: Ignore transliteration errors setting."""
        return self._ignore_errors

    @ignore_errors.setter
    def ignore_errors(self, value):
        self._ignore_errors = value

    @property
    def last_matched_rules(self):
        """
        `list` of `TransliterationRule`: Last transliteration rules matched.
        """
        return [self._rules[_] for _ in self._rule_keys]

    @property
    def last_matched_rule_tokens(self):
        """`list` of `list` of `str`: Last matched tokens for each rule."""
        return [self._rules[_].tokens for _ in self._rule_keys]

    @property
    def last_input_tokens(self):
        """
        `list` of `str`: Last tokenization of the input string, with whitespace
        at start and end."""
        return self._input_tokens

    @property
    def metadata(self):
        """
        `dict`: Metadata of transliterator
        """
        return self._metadata

    @property
    def onmatch_rules_lookup(self):
        """
        `dict`: On Match Rules lookup
        """
        return self._onmatch_rules_lookup

    @property
    def tokenizer_pattern(self):
        """
        `str`: Tokenizer pattern from transliterator
        """
        return self._tokenizer_pattern

    @property
    def tokens_by_class(self):
        """
        `dict` of {`str`: `list` of `str`}: Tokenizer pattern from transliterator
        """
        return self._tokens_by_class

    def transliterate(self, input):
        """
        Transliterate an input string into an output string.

        Parameters
        ----------
        input : `str`
            Input string to transliterate

        Returns
        -------
        `str`
            Transliteration output string

        Raises
        ------
        ValueError
            Cannot parse input

        Note
        ----
        Whitespace will be temporarily appended to start and end of input
        string.

        Example
        -------

        .. jupyter-execute::

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

        """
        tokens = self.tokenize(input)  # Adds initial+final whitespace
        self._input_tokens = tokens  # Tokens are saved here
        self._rule_keys = []  # Matched ule keys are saved here
        output = ""
        token_i = 1  # Adjust for initial whitespace

        while token_i < len(tokens) - 1:  # Adjust for final whitespace
            rule_key = self.match_at(token_i, tokens)
            if rule_key is None:
                logger.warning(
                    "No matching transliteration rule at token pos %s of %s"
                    % (token_i, tokens)
                )
                # No parsing rule was found at this location
                if self.ignore_errors:
                    # Move along if ignoring errors
                    token_i += 1
                    continue
                else:
                    raise NoMatchingTransliterationRuleException
            self._rule_keys.append(rule_key)
            rule = self.rules[rule_key]
            tokens_matched = rule.tokens
            if self._onmatch_rules:
                curr_match_rules = None
                prev_t = tokens[token_i - 1]
                curr_t = tokens[token_i]
                curr_t_rules = self._onmatch_rules_lookup.get(curr_t)
                if curr_t_rules:
                    curr_match_rules = curr_t_rules.get(prev_t)
                if curr_match_rules:
                    for onmatch_i in curr_match_rules:
                        onmatch = self._onmatch_rules[onmatch_i]
                        # <class_a> <class_a> + <class_b>
                        # a a b
                        #     ^
                        # ^      - len(onmatch.prev_rules)
                        if self._match_tokens(
                            token_i - len(onmatch.prev_classes),
                            onmatch.prev_classes,  # Checks last value
                            tokens,
                            check_prev=True,
                            check_next=False,
                            by_class=True,
                        ) and self._match_tokens(
                            token_i,
                            onmatch.next_classes,  # Checks first value
                            tokens,
                            check_prev=False,
                            check_next=True,
                            by_class=True,
                        ):
                            output += onmatch.production
                            break  # Only match best onmatch rule
            output += rule.production
            token_i += len(tokens_matched)
        return output

    def tokenize(self, input):
        """
        Tokenizes an input string.

        Adds initial and trailing whitespace, which can be consolidated.

        Parameters
        ----------
        input : str
            String to tokenize

        Returns
        -------
        `list` of `str`
            List of tokens, with default whitespace token at beginning and end.

        Raises
        ------
        ValueError
            Unrecognizable input, such as a character that is not in a token

        Examples
        --------
        .. jupyter-execute::

          tokens = {'ab': ['class_ab'], ' ': ['wb']}
          whitespace = {'default': ' ', 'token_class': 'wb', 'consolidate': True}
          rules = {'ab': 'AB', ' ': '_'}
          settings = {'tokens': tokens, 'rules': rules, 'whitespace': whitespace}
          gt = GraphTransliterator.from_easyreading_dict(settings)
          gt.tokenize('ab ')

        """

        def is_whitespace(token):
            """Check if token is whitespace."""
            return self.whitespace.token_class in self.tokens[token]

        # start with a whitespace token
        tokens = [self.whitespace.default]

        prev_whitespace = True

        match_at = 0
        while match_at < len(input):
            match = self._tokenizer.match(input, match_at)
            if match:
                match_at = match.end()  # advance match_at
                token = match.group(0)
                # Could save match loc here:
                # matched_at = match.span(0)[0]
                if is_whitespace(token):
                    if prev_whitespace and self.whitespace.consolidate:
                        continue
                    else:
                        prev_whitespace = True
                else:
                    prev_whitespace = False
                tokens.append(token)
            else:
                logger.warning(
                    "Unrecognizable token %s at pos %s of %s"
                    % (input[match_at], match_at, input)
                )
                if not self.ignore_errors:
                    raise UnrecognizableInputTokenException
                else:
                    match_at += 1

        if self.whitespace.consolidate:
            while len(tokens) > 1 and is_whitespace(tokens[-1]):
                tokens.pop()

        tokens.append(self.whitespace.default)

        assert len(tokens) >= 2  # two whitespaces, at least

        return tokens

    def pruned_of(self, productions):
        """
        Remove transliteration rules with specific output productions.

        Parameters
        ----------
        productions : `str`, or `list` of `str`
            list of productions to remove

        Returns
        -------
        graphtransliterator.GraphTransliterator
            Graph transliterator pruned of certain productions.

        Note
        ----
        Uses original initialization parameters to construct a new
        :class:`GraphTransliterator`.

        Examples
        --------
        .. jupyter-execute::

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
          gt.rules

        .. jupyter-execute::

          gt.pruned_of('<AA>').rules

        .. jupyter-execute::

          gt.pruned_of(['<A>', '<AA>']).rules

        """  # noqa
        pruned_rules = [_ for _ in self._rules if _.production not in productions]
        return GraphTransliterator(
            self._tokens,
            pruned_rules,
            self._whitespace,
            onmatch_rules=self._onmatch_rules,
            metadata=self._metadata,
            ignore_errors=self._ignore_errors,
            check_ambiguity=self._check_ambiguity,
        )

    @property
    def productions(self):
        """
        `list` of `str`: List of productions of each transliteration rule.
        """
        return [_.production for _ in self.rules]

    @property
    def tokens(self):
        """
        `dict` of {`str`:`set` of `str`}: Mappings of tokens to their classes.
        """
        return self._tokens

    @property
    def rules(self):
        """
        `list` of `TransliterationRule`: Transliteration rules sorted by cost.
        """
        return self._rules

    @property
    def onmatch_rules(self):
        """`list` of :class:`OnMatchRules`: Rules for productions between matches."""
        return self._onmatch_rules

    @property
    def whitespace(self):
        """WhiteSpaceRules: Whitespace rules."""
        return self._whitespace

    @classmethod
    def from_dict(cls, dict_settings, **kwargs):
        """Generate GraphTransliterator from `dict` settings.

        Parameters
        ----------
        dict_settings : `dict`
            Dictionary of settings

        Returns
        -------
        GraphTransliterator
            Graph transliterator
        """
        settings = SettingsSchema().load(dict_settings)
        return cls(
            settings["tokens"],
            settings["rules"],
            settings["whitespace"],
            onmatch_rules=settings.get("onmatch_rules"),
            metadata=settings.get("metadata"),
            tokens_by_class=settings.get("tokens_by_class"),  # will be generated
            graph=settings.get("graph"),  # will be generated
            tokenizer_pattern=settings.get("tokenizer_pattern"),  # will be generated
            ignore_errors=kwargs.get("ignore_errors", False),
            check_ambiguity=kwargs.get("check_ambiguity", True),
        )

    @classmethod
    def from_easyreading_dict(cls, easyreading_settings, **kwargs):
        """
        Constructs `GraphTransliterator` from a dictionary of settings in
        "easy reading" format, i.e. the loaded contents of a YAML string.

        Parameters
        ----------
        easyreading_settings : `dict`
            Settings dictionary in easy reading format with keys:

                ``"tokens"``
                  Mappings of tokens to their classes
                  (`dict` of {str: `list` of `str`})

                ``"rules"``
                  Transliteration rules in "easy reading" format
                  (`list` of `dict` of {`str`: `str`})

                ``"onmatch_rules"``
                  On match rules in "easy reading" format
                  (`dict` of {`str`: `str`}, optional)

                ``"whitespace"``
                  Whitespace definitions, including default whitespace token,
                  class of whitespace tokens, and whether or not to consolidate
                  (`dict` of {'default': `str`, 'token_class': `str`,
                  consolidate: `bool`}, optional)

                ``"metadata"``
                  Dictionary of metadata (`dict`, optional)

        Returns
        -------
        GraphTransliterator
            Graph Transliterator

        Note
        ----
        Called by :meth:`from_yaml`.

        Example
        -------
        .. jupyter-execute::

          tokens = {
              'ab': ['class_ab'],
              ' ': ['wb']
          }
          whitespace = {
              'default': ' ',
              'token_class': 'wb',
              'consolidate': True
          }
          onmatch_rules = [
              {'<class_ab> + <class_ab>': ','}
          ]
          rules = {'ab': 'AB',
                   ' ': '_'}
          settings = {'tokens': tokens,
                      'rules': rules,
                      'whitespace': whitespace,
                      'onmatch_rules': onmatch_rules}
          gt = GraphTransliterator.from_easyreading_dict(settings)
          gt.transliterate("ab abab")


        See Also
        --------
        from_yaml : Constructor from YAML string in "easy reading" format
        from_yaml_file : Constructor from YAML file in "easy reading" format
        """
        # Validate easyreading settings
        _ = EasyReadingSettingsSchema().load(easyreading_settings)
        # Convert those to regular settings
        _ = _process_easyreading_settings(_)
        # Validation of regular settings is done in from_dict
        return cls.from_dict(_, **kwargs)

    @classmethod
    def from_yaml(cls, yaml_str, charnames_escaped=True, **kwargs):
        """
        Construct GraphTransliterator from a YAML str.

        Parameters
        ----------
        yaml_str : str
            YAML mappings of tokens, rules, and (optionally) onmatch_rules
        charnames_escaped : boolean
            Unescape Unicode during YAML read (default True)

        Note
        ----
        Called by :meth:`from_yaml_file` and calls :meth:`from_easyreading_dict`.

        Example
        -------
        .. jupyter-execute::

          yaml_ = '''
          tokens:
            a: [class1]
            ' ': [wb]
          rules:
            a: A
            ' ': ' '
          whitespace:
            default: ' '
            consolidate: True
            token_class: wb
          onmatch_rules:
            - <class1> + <class1>: "+"
          '''
          gt = GraphTransliterator.from_yaml(yaml_)
          gt.transliterate("a aa")


        See Also
        --------
        from_easyreading_dict : Constructor from dictionary in "easy reading" format
        from_yaml : Constructor from YAML string in "easy reading" format
        from_yaml_file : Constructor from YAML file in "easy reading" format
        """
        if charnames_escaped:
            yaml_str = _unescape_charnames(yaml_str)

        settings = yaml.safe_load(yaml_str)

        return cls.from_easyreading_dict(settings, **kwargs)

    @classmethod
    def from_yaml_file(cls, yaml_filename, **kwargs):
        """
        Construct GraphTransliterator from YAML file.

        Parameters
        ----------
        yaml_filename : str
            Name of YAML file, containing tokens, rules, and (optionally)
            onmatch_rules

        Note
        ----
        Calls :meth:`from_yaml`.

        See Also
        --------
        from_yaml : Constructor from YAML string in "easy reading" format
        from_easyreading_dict : Constructor from dictionary in "easy reading" format
        """
        with open(yaml_filename, "r") as f:
            yaml_string = f.read()

        return cls.from_yaml(yaml_string, **kwargs)

    def dumps(self):
        """
        Dump settings of Graph Transliterator to Javascript Object Notation (JSON).

        Returns
        -------
        `str`
            JSON string

        Examples
        --------
        .. jupyter-execute::

          yaml_ = '''
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
              - <vowel> + <vowel>: ','  # add a comma between vowels
            metadata:
              author: "Author McAuthorson"
          '''
          gt = GraphTransliterator.from_yaml(yaml_)
          gt.dumps()


        See Also
        --------
        dump : Dump Graph Transliterator configuration to Python data types
        load : Load Graph Transliteration from configuration in Python data types
        loads : Load Graph Transliteration from configuration as a JSON string
        """  # noqa

        return GraphTransliteratorSchema().dumps(self)

    def dump(self):
        """
        Dump configuration of Graph Transliterator to Python data types.

        Returns
        -------
        OrderedDict
            GraphTransliterator configuration as a dictionary with keys:

                ``"tokens"``
                  Mappings of tokens to their classes
                  (`OrderedDict` of {str: `list` of `str`})

                ``"rules"``
                  Transliteration rules in direct format
                  (`list` of `dict` of {`str`: `str`})

                ``"whitespace"``
                  Whitespace settings
                  (`dict` of {`str`: `str`})

                ``"onmatch_rules"``
                  On match rules
                  (`list` of `OrderedDict`)

                ``"metadata"``
                  Dictionary of metadata (`dict`)

                ``"ignore_errors"``
                  Ignore errors in transliteration (`bool`)

                ``"onmatch_rules_lookup"``
                  Dictionary keyed by current token to previous token
                  containing a list of indexes of applicable :class:`OnmatchRule`
                  to try
                  (`dict` of {`str`: `dict` of {`str`: `list` of `int`}})

                ``"tokens_by_class"``
                  Tokens keyed by token class, used internally
                  (`dict` of {`str`: `list` of str})

                ``"graph"``
                  Serialization of `DirectedGraph`
                  (`dict`)

                ``"tokenizer_pattern"``
                  Regular expression for tokenizing
                  (`str`)

                ``"graphtransliterator_version"``
                  Module version of `graphtransliterator` (`str`)

        Example
        -------
        .. jupyter-execute::

          yaml_ = '''
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
            - <vowel> + <vowel>: ','  # add a comma between vowels
          metadata:
            author: "Author McAuthorson"
          '''
          gt = GraphTransliterator.from_yaml(yaml_)
          gt.dump()


        See Also
        --------
        dumps : Dump Graph Transliterator configuration to JSON string
        load : Load Graph Transliteration from configuration in Python data types
        loads : Load Graph Transliteration from configuration as a JSON string

"""  # noqa
        return GraphTransliteratorSchema().dump(self)

    @staticmethod
    def load(settings, **kwargs):
        """Create GraphTransliterator from settings as Python data types.

        Parameters
        ----------
        settings
            GraphTransliterator configuration as a dictionary with keys:

                ``"tokens"``
                  Mappings of tokens to their classes
                  (`dict` of {str: `list` of `str`})

                ``"rules"``
                  Transliteration rules in direct format
                  (`list` of `OrderedDict` of {`str`: `str`})

                ``"whitespace"``
                  Whitespace settings
                  (`dict` of {`str`: `str`})

                ``"onmatch_rules"``
                  On match rules
                  (`list` of `OrderedDict`, optional)

                ``"metadata"``
                  Dictionary of metadata (`dict`, optional)

                ``"ignore_errors"``
                  Ignore errors. (`bool`, optional)

                ``"onmatch_rules_lookup"``
                  Dictionary keyed by current token to previous token
                  containing a list of indexes of applicable :class:`OnmatchRule`
                  to try
                  (`dict` of {`str`: `dict` of {`str`: `list` of `int`}}, optional)

                ``tokens_by_class``
                  Tokens keyed by token class, used internally
                  (`dict` of {`str`: `list` of str}, optional)

                ``graph``
                  Serialization of `DirectedGraph`
                  (`dict`, optional)

                ``"tokenizer_pattern"``
                  Regular expression for tokenizing
                  (`str`, optional)

                ``"graphtransliterator_version"``
                  Module version of `graphtransliterator` (`str`, optional)

        Returns
        -------
        GraphTransliterator
            Graph Transliterator

        Example
        -------
        .. jupyter-execute::

          from collections import OrderedDict
          settings = \
          {'tokens': {'a': ['vowel'], ' ': ['wb']},
           'rules': [OrderedDict([('production', 'A'),
                         # Can be compacted, removing None values
                         # ('prev_tokens', None),
                         ('tokens', ['a']),
                         ('next_classes', None),
                         ('next_tokens', None),
                         ('cost', 0.5849625007211562)]),
            OrderedDict([('production', ' '),
                         ('prev_classes', None),
                         ('prev_tokens', None),
                         ('tokens', [' ']),
                         ('next_classes', None),
                         ('next_tokens', None),
                         ('cost', 0.5849625007211562)])],
           'whitespace': {'default': ' ', 'token_class': 'wb', 'consolidate': False},
           'onmatch_rules': [OrderedDict([('prev_classes', ['vowel']),
                         ('next_classes', ['vowel']),
                         ('production', ',')])],
           'metadata': {'author': 'Author McAuthorson'},
           'onmatch_rules_lookup': {'a': {'a': [0]}},
           'tokens_by_class': {'vowel': ['a'], 'wb': [' ']},
           'graph': {'edge': {0: {1: {'token': 'a', 'cost': 0.5849625007211562},
              3: {'token': ' ', 'cost': 0.5849625007211562}},
             1: {2: {'cost': 0.5849625007211562}},
             3: {4: {'cost': 0.5849625007211562}}},
            'node': [{'type': 'Start', 'ordered_children': {'a': [1], ' ': [3]}},
             {'type': 'token', 'token': 'a', 'ordered_children': {'__rules__': [2]}},
             {'type': 'rule',
              'rule_key': 0,
              'rule': OrderedDict([('production', 'A'),
                           ('prev_classes', None),
                           ('prev_tokens', None),
                           ('tokens', ['a']),
                           ('next_tokens', None),
                           ('next_classes', None),
                           ('cost', 0.5849625007211562)]),
              'accepting': True,
              'ordered_children': {}},
             {'type': 'token', 'token': ' ', 'ordered_children': {'__rules__': [4]}},
             {'type': 'rule',
              'rule_key': 1,
              'rule': OrderedDict([('production', ' '),
                           # Can be compacted, removing None values
                           # ('prev_tokens', None),
                           ('tokens', [' ']),
                           ('next_tokens', None),
                           ('next_classes', None),
                           ('cost', 0.5849625007211562)]),
              'accepting': True,
              'ordered_children': {}}],
            'edge_list': [(0, 1), (1, 2), (0, 3), (3, 4)]},
           'tokenizer_pattern': '(a|\\ )',
           'graphtransliterator_version': '0.3.3'}
          gt = GraphTransliterator.load(settings)
          gt.transliterate('aa')

        .. jupyter-execute::

          # can be compacted
          settings.pop('onmatch_rules_lookup')
          GraphTransliterator.load(settings).transliterate('aa')


        See Also
        --------
        dump : Dump Graph Transliterator configuration to Python data types
        dumps : Dump Graph Transliterator configuration to JSON string
        loads : Load Graph Transliteration from configuration as a JSON string
        """  # noqa
        # combine kwargs with settings
        return GraphTransliteratorSchema().load(dict(settings, **kwargs))

    @staticmethod
    def loads(settings, **kwargs):
        """Create GraphTransliterator from JavaScript Object Notation (JSON) string.

        Parameters
        ----------
        settings
            JSON settings for GraphTransliterator

        Returns
        -------
        GraphTransliterator
            Graph Transliterator

        Example
        -------
        .. jupyter-execute::

          JSON_settings = '''{"tokens": {"a": ["vowel"], " ": ["wb"]}, "rules": [{"production": "A", "prev_classes": null, "prev_tokens": null, "tokens": ["a"], "next_classes": null, "next_tokens": null, "cost": 0.5849625007211562}, {"production": " ", "prev_classes": null, "prev_tokens": null, "tokens": [" "], "next_classes": null, "next_tokens": null, "cost": 0.5849625007211562}], "whitespace": {"default": " ", "token_class": "wb", "consolidate": false}, "onmatch_rules": [{"prev_classes": ["vowel"], "next_classes": ["vowel"], "production": ","}], "metadata": {"author": "Author McAuthorson"}, "ignore_errors": false, "onmatch_rules_lookup": {"a": {"a": [0]}}, "tokens_by_class": {"vowel": ["a"], "wb": [" "]}, "graph": {"node": [{"type": "Start", "ordered_children": {"a": [1], " ": [3]}}, {"type": "token", "token": "a", "ordered_children": {"__rules__": [2]}}, {"type": "rule", "rule_key": 0, "rule": {"production": "A", "prev_classes": null, "prev_tokens": null, "tokens": ["a"], "next_tokens": null, "next_classes": null, "cost": 0.5849625007211562}, "accepting": true, "ordered_children": {}}, {"type": "token", "token": " ", "ordered_children": {"__rules__": [4]}}, {"type": "rule", "rule_key": 1, "rule": {"production": " ", "prev_classes": null, "prev_tokens": null, "tokens": [" "], "next_tokens": null, "next_classes": null, "cost": 0.5849625007211562}, "accepting": true, "ordered_children": {}}], "edge": {"0": {"1": {"token": "a", "cost": 0.5849625007211562}, "3": {"token": " ", "cost": 0.5849625007211562}}, "1": {"2": {"cost": 0.5849625007211562}}, "3": {"4": {"cost": 0.5849625007211562}}}, "edge_list": [[0, 1], [1, 2], [0, 3], [3, 4]]}, "tokenizer_pattern": "(a| )", "graphtransliterator_version": "1.0.0"}'''

          gt = GraphTransliterator.loads(JSON_settings)
          gt.transliterate('a')

        See Also
        --------
        dump : Dump Graph Transliterator configuration to Python data types
        dumps : Dump Graph Transliterator configuration to JSON string
        load : Load Graph Transliteration from configuration in Python data types
        """  # noqa
        # combine kwargs with settings
        _settings = dict(json.loads(settings), **kwargs)
        return GraphTransliteratorSchema().load(_settings)


def check_for_ambiguity(transliterator):
    """
    Check if multiple transliteration rules could match the same tokens.

    This function first groups the transliteration rules by number of
    tokens. It then checks to see if any pair of the same cost would match
    the same sequence of tokens. If so, it finally checks if a less costly
    rule would match those particular sequences. If not, there is
    ambiguity.

    Details of all ambiguity are sent in a :func:`logging.warning`.

    Note
    ----
    Called during initialization if ``check_ambiguity`` is set.

    Raises
    ------
    AmbiguousTransliterationRulesException
        Multiple transliteration rules could match the same tokens.

    Example
    -------
    .. jupyter-execute::

      yaml_filename = '''
      tokens:
        a: [class1, class2]
        ' ': [wb]
      rules:
        <class1> a: AW
        <class2> a: AA # ambiguous rule
      whitespace:
        default: ' '
        consolidate: True
        token_class: wb
      '''
      gt = GraphTransliterator.from_yaml(yaml_, check_ambiguity=False)
      gt.check_for_ambiguity()

    """
    ambiguity = False

    all_tokens = set(transliterator._tokens.keys())

    rules = transliterator._rules

    if not rules:
        return True

    max_prev = [_count_of_prev(rule) for rule in rules]
    global_max_prev = max(max_prev)
    max_curr_next = [_count_of_curr_and_next(rule) for rule in rules]
    global_max_curr_next = max(max_curr_next)

    # Generate a matrix of rules, where width is the max of
    # any previous tokens/classes + max of current/next tokens/classes.
    # Each rule's specifications starting from the max of the previous
    # tokens/classes. Other positions are filled by the set of all possible
    # tokens.

    matrix = []

    width = global_max_prev + global_max_curr_next

    for i, rule in enumerate(rules):
        row = [all_tokens] * (global_max_prev - max_prev[i])
        row += _tokens_possible(rule, transliterator._tokens_by_class)
        row += [all_tokens] * (width - len(row))
        matrix += [row]

    def full_intersection(i, j):
        """ Intersection of  matrix[i] and matrix[j], else None."""

        intersections = []
        for k in range(width):
            intersection = matrix[i][k].intersection(matrix[j][k])
            if not intersection:
                return None
            intersections += [intersection]
        return intersections

    def covered_by(intersection, row):
        """Check if intersection is covered by row."""
        for i in range(len(intersection)):
            diff = intersection[i].difference(row[i])
            if diff:
                return False
        return True

    # Iterate through rules based on cost (number of tokens). If there are
    # ambiguities, then see if a less costly rule would match the rule. If it does
    # not, there is ambiguity.

    for _group_val, group_iter in itertools.groupby(
        enumerate(transliterator._rules), key=lambda x: x[1].cost
    ):

        group = list(group_iter)
        if len(group) == 1:
            continue
        for i in range(len(group) - 1):
            for j in range(i + 1, len(group)):
                i_index = group[i][0]
                j_index = group[j][0]
                intersection = full_intersection(i_index, j_index)
                if not intersection:
                    break

                # Check if a less costly rule matches intersection

                def covered_by_less_costly():
                    for r_i, rule in enumerate(rules):
                        if r_i in (i_index, j_index):
                            continue
                        if rule.cost > rules[i_index].cost:
                            continue
                        rule_tokens = matrix[r_i]
                        if covered_by(intersection, rule_tokens):
                            return True
                    return False

                if not covered_by_less_costly():
                    logging.warning(
                        "The pattern {} can be matched by both:\n"
                        "  {}\n"
                        "  {}\n".format(
                            intersection,
                            _easyreading_rule(rules[i_index]),
                            _easyreading_rule(rules[j_index]),
                        )
                    )
                    ambiguity = True
    if ambiguity:
        raise AmbiguousTransliterationRulesException


def _easyreading_rule(rule):
    """Get an easy-reading string of a rule."""

    def _token_str(x):
        return " ".join(x)

    def _class_str(x):
        return " ".join(["<%s>" % _ for _ in x])

    out = ""
    if rule.prev_classes and rule.prev_tokens:
        out = "({} {}) ".format(
            _class_str(rule.prev_classes), _token_str(rule.prev_tokens)
        )
    elif rule.prev_classes:
        out = "{} ".format(_class_str(rule.prev_classes))
    elif rule.prev_tokens:
        out = "({}) ".format(_token_str(rule.prev_tokens))

    out += _token_str(rule.tokens)

    if rule.next_tokens and rule.next_classes:
        out += " ({} {})".format(
            _token_str(rule.next_tokens), _class_str(rule.next_classes)
        )
    elif rule.next_tokens:
        out += " ({})".format(_token_str(rule.next_tokens))
    elif rule.next_classes:
        out += " {}".format(_class_str(rule.next_classes))
    return out


def _count_of_prev(rule):
    """Count previous tokens to be present before a match in a rule."""

    return len(rule.prev_classes or []) + len(rule.prev_tokens or [])


def _count_of_curr_and_next(rule):
    """Count tokens to be matched and those to follow them in rule."""

    return len(rule.tokens) + len(rule.next_tokens or []) + len(rule.next_classes or [])


def _prev_tokens_possible(rule, tokens_by_class):
    """`list` of set of possible preceding tokens for a rule."""

    return [tokens_by_class[_] for _ in rule.prev_classes or []] + [
        set([_]) for _ in rule.prev_tokens or []
    ]


def _curr_and_next_tokens_possible(rule, tokens_by_class):
    """`list` of sets of possible current and following tokens for a rule."""

    return (
        [set([_]) for _ in rule.tokens]
        + [set([_]) for _ in rule.next_tokens or []]
        + [tokens_by_class[_] for _ in rule.next_classes or []]
    )


def _tokens_possible(row, tokens_by_class):
    """`list` of sets of possible tokens matched for a rule."""

    return _prev_tokens_possible(row, tokens_by_class) + _curr_and_next_tokens_possible(
        row, tokens_by_class
    )


# Initialization-related functions for unescaping Unicode


def _unescape_charnames(input_str):
    r"""
    Convert \\N{Unicode charname}-escaped str to unicode characters.

    This is useful for specifying exact character names, and a default
    escape feature in Python that needs a function to be used for reading
    from files.

    Parameters
    ----------
    input_str : str
        The unescaped string, with \\N{Unicode charname} converted to
        the corresponding Unicode characters.

    Examples
    --------

    .. jupyter-execute::

      GraphTransliterator._unescape_charnames(r"H\N{LATIN SMALL LETTER I}")

    """

    def get_unicode_char(matchobj):
        """Get Unicode character value from escaped character sequences."""
        charname = matchobj.group(0)
        match = re.match(r"\\N{([-A-Z ]+)}", charname)
        char = unicodedata.lookup(match.group(1))  # KeyError if invalid
        return char

    return re.sub(r"\\N{[-A-Z ]+}", get_unicode_char, input_str)


class CoverageTransliterator(GraphTransliterator):
    """Subclass of GraphTransliterator that logs visits to graph and on_match rules.

    Used to confirm that tests cover the entire graph and onmatch_rules."""

    def __init__(self, *args, **kwargs):
        # Initialize from GraphTransliterator
        GraphTransliterator.__init__(self, *args, **kwargs)
        # Convert  _graph and _onmatch_rules to visit-tracking objects
        self._graph = VisitLoggingDirectedGraph(self._graph)
        self._onmatch_rules = VisitLoggingList(self._onmatch_rules)

    def clear_visited(self):
        """Clear visited flags from graph and onmatch_rules."""
        self._graph.clear_visited()
        if self._onmatch_rules:
            self._onmatch_rules.clear_visited()

    def check_onmatchrules_coverage(self, raise_exception=True):
        """Check coverage of onmatch rules."""
        errors = []
        onmatch_rules = self._onmatch_rules
        for i, onmatch_rule in enumerate(onmatch_rules.data):  # data to avoid visited
            if i not in onmatch_rules.visited:
                logger.warning(
                    "On Match Rule {} [{}] has not been visited.".format(
                        i, onmatch_rule
                    )
                )
                errors.append(i)
        if errors and raise_exception:
            error_msg = "Missed OnMatchRules: " + ",".join([str(i) for i in errors])
            raise IncompleteOnMatchRulesCoverageException(error_msg)
        return not errors

    def check_coverage(self, raise_exception=True):
        """Check coverage of graph and onmatch rules.

        First checks graph coverage, then checks onmatch rules."""

        return self._graph.check_coverage(
            raise_exception=raise_exception
        ) and self.check_onmatchrules_coverage(raise_exception=raise_exception)
