# -*- coding: utf-8 -*-

"""GraphTransliterator main module."""

from collections import deque
import logging
import re
import unicodedata
import yaml
from .validate import validate_raw_settings, validate_settings
from .process import _process_settings
from .initialize import (
    _tokens_of, _transliteration_rule_of, _whitespace_of, _onmatch_rule_of,
    _onmatch_rules_lookup, _tokenizer_from, _graph_from
)
from .exceptions import (
    NoMatchingTransliterationRule,
    UnrecognizableInputToken
)

logger = logging.getLogger('graphtransliterator')


class GraphTransliterator:
    """
    Graph-based transliteration tool.

    GraphTransliterator constructs a graph that
    can be used to transliterate the tokens of an input
    string into an output string, e.g. moving from one
    language's alphabet to another. Once initialized, it also offers a
    transliterate function, as well as the ability to output the constructed
    graph.

    GraphTransliterates takes as an initialization parameter the acceptable
    tokens, e.g. "g" or "gh", of an input string and also a list of the
    tokens' classes, e.g. "consonant or "whitespace.""

    GraphTransliterator allows for context-sensitive matching based on a list
    of transliteration rules. When a defined sequence of tokens is
    matched on an input string, a defined output is produced. Rules can also
    require specific tokens to precede or follow the token sequence, or by
    tokens of a specific class(before the previous/following tokens,
    if specified).

    Transliteration rules are automatically ordered so that the most exact
    match is returned by default. Internally, this ordering is done by
    assigning a cost to each edge of the graph. Edges leading to more specific
    matches, e.g. the token sequence "aa" instead of just "a," cost less and
    are tried first. Tokens cost slightly less than token classes.

    GraphTransliterator can also insert a string between combinations of
    particular token classes.

    GraphTransliterator is parameterized  by a specific token type as its
    default token for whitespace (usually " "), which can be optionally
    consolidated in the output string.

    GraphTransliterator can be initialized from an easy-to-read YAML format or
    directly from a dictionary. Parameters are rigorously validated.
    """

    def __init__(self, tokens, rules, onmatch_rules, whitespace, metadata,
                 ignore_exceptions=True, **kwargs):
        validate_settings(tokens, rules, onmatch_rules, whitespace, metadata)
        self._metadata = metadata
        self._tokens = _tokens_of(tokens)
        self._rules = sorted(
            [_transliteration_rule_of(rule) for rule in rules],
            key=lambda transliteration_rule: transliteration_rule.cost)
        self._onmatch_rules = [_onmatch_rule_of(_) for _ in onmatch_rules]
        self._onmatch_rules_lookup = \
            _onmatch_rules_lookup(tokens, self._onmatch_rules)
        self._whitespace = _whitespace_of(whitespace)
        if not type(ignore_exceptions) == bool:
            raise ValueError("ignore_expections is not a boolean.")
        self._ignore_exceptions = ignore_exceptions
        self.__init_parameters__ = {     # used by pruned_of
            'tokens': tokens,
            'rules': rules,
            'onmatch_rules': onmatch_rules,
            'whitespace': whitespace,
            'metadata': metadata,
            'kwargs': kwargs,
        }
        self._tokenizer = _tokenizer_from(list(tokens.keys()))
        self._graph = _graph_from(self.rules)
        # self._input_tokens = None
        self._rule_keys = []  # last matched rules

    def _match_constraints(self, source, target, token_i, tokens):
        """
        Match edge constraints.

        Called on edge before a rule. `token_i` is set to location right
        after tokens consumed.

        """
        target_edge = self._graph.edge[source][target]

        constraints = target_edge.get('constraints')

        if not constraints:
            return True
        # should these be ordered?
        for c_type, c_value in constraints.items():
            # logger.debug("Constraints::c_type: %s c_value: %s" %
            #     (c_type, c_value))
            if c_type == 'prev_tokens':
                num_tokens = len(self._graph.node[target]['rule'].tokens)
                # presume for rule (a) a, with input "aa"
                # ' ', a, a, ' '  start (token_i=3)
                #             ^
                #         ^       -1 subtract num_tokens
                #      ^          - len(c_value)
                start_at = token_i
                start_at -= num_tokens
                start_at -= len(c_value)

                if not self._match_tokens(start_at, c_value,
                                          tokens,
                                          check_prev=True, check_next=False,
                                          by_class=False):
                    return False
            elif c_type == 'next_tokens':
                # presume for rule a (a), with input "aa"
                # ' ', a, a, ' '  start (token_i=2)
                #         ^
                start_at = token_i

                if not self._match_tokens(start_at, c_value,
                                          tokens,
                                          check_prev=False, check_next=True,
                                          by_class=False):
                    return False

            elif c_type == 'prev_classes':
                num_tokens = len(self._graph.node[target]['rule'].tokens)
                # presume for rule (a <class_a>) a, with input "aaa"
                # ' ', a, a, a, ' '
                #                ^     start (token_i=4)
                #            ^         -num_tokens
                #         ^            -len(prev_tokens)
                #  ^                   -len(prev_classes)
                start_at = token_i
                start_at -= num_tokens
                prev_tokens = constraints.get('prev_tokens')
                if prev_tokens:
                    start_at -= len(prev_tokens)
                start_at -= len(c_value)
                if not self._match_tokens(start_at, c_value,
                                          tokens,
                                          check_prev=True, check_next=False,
                                          by_class=True):
                    return False

            elif c_type == 'next_classes':
                # presume for rule a (a <class_a>), with input "aaa"
                # ' ', a, a, a, ' '
                #         ^          start (token_i=2)
                #            ^       + len of next_tokens (a)
                start_at = token_i
                next_tokens = constraints.get('next_tokens')
                if next_tokens:
                    start_at += len(next_tokens)
                if not self._match_tokens(start_at, c_value,
                                          tokens,
                                          check_prev=False, check_next=True,
                                          by_class=True):
                    return False

        # logger.debug("Matched constraints! %s:%s" % (c_type, c_value))#
        return True

    def match_at(self, token_i, tokens, match_all=False):
        """
        Match best (least costly) transliteration rule at `token_i`.

        Parameters
        ----------
        token_i : int
            Location in tokens at which to begin
        match_all : bool
            Report all possible matches, not just the best one.
        tokens : list
            List of tokens
        Notes
        -----
        Expects and requires whitespace token at beginning and end of tokens.
        Performs a best-first search by maintaining a stack that consists
        of a tuple of node_key, parent_key, and token_i.

        Returns
        -------
        int
            Rule index
        """

        graph = self._graph
        if match_all:
            matches = []
        stack = deque()

        def _append_children(node_key, token_i):
            children = None
            ordered_children = graph.node[node_key].get('ordered_children')
            if ordered_children:
                children = ordered_children.get(tokens[token_i])
                if children:
                    # reordered high to low for stack:
                    for child_key in reversed(children):
                        stack.appendleft(
                            (child_key, node_key, token_i)
                        )
                else:
                    rules_keys = ordered_children.get('__rules__')  # leafs
                    if rules_keys:
                        # There may be more than one as certain rules have
                        # constraints on them.
                        # reordered so high cost go on stack last
                        for rule_key in reversed(rules_keys):
                            stack.appendleft((rule_key, node_key, token_i))
        _append_children(0, token_i)  # append all children of root node

        while stack:  # LIFO
            node_key, parent_key, token_i = stack.popleft()
            assert token_i < len(tokens), "way past boundary"
            curr_node = graph.node[node_key]
            # check constraints on preceding edge
            if curr_node.get('accepting') and \
               self._match_constraints(parent_key, node_key, token_i, tokens):
                if match_all:
                    matches.append(curr_node['rule_key'])
                    continue
                else:
                    return curr_node['rule_key']
            else:
                if token_i < len(tokens)-1:
                    token_i += 1
                _append_children(node_key, token_i)
        if match_all:
            # logger.debug("matched: %s " % matches)
            return matches

    def _match_tokens(self, start_i, c_value, tokens, check_prev=True,
                      check_next=True, by_class=False):
        """Match tokens, with boundary checks."""

        if check_prev and start_i < 0:
            return False
        if check_next and start_i + len(c_value) > len(tokens):
            return False
        for i in range(0, len(c_value)):
            if by_class:
                if not c_value[i] in self._tokens[tokens[start_i+i]]:
                    return False
            elif tokens[start_i+i] != c_value[i]:
                return False
        return True

    @property
    def ignore_exceptions(self):
        """Get ignore exceptions setting."""
        return self._ignore_exceptions

    @ignore_exceptions.setter
    def ignore_exceptions(self, value):
        if type(value) is not bool:
            raise ValueError("ignore_exceptions must be a boolean.")
        self._ignore_exceptions = value

    @property
    def last_matched_rules(self):
        """
        Get last matched rules.

        Returns
        -------
        list of TransliterationRule
            list of TransliterationRule for the previously matched rules,
            or an empty list.

        """
        return [self._rules[_] for _ in self._rule_keys]

    @property
    def last_matched_tokens(self):
        """
        Get last matched tokens for each rule.

        Returns
        -------
        list of str
            list of tokens for the previously matched rules,
            or an empty list.

        """
        return [self._rules[_].tokens for _ in self._rule_keys]

    def transliterate(self, input):
        """
        Transliterate an input str into an output str.

        Parameters
        ----------
        input : str
            String to transliterate

        Returns
        -------
        str
            Transliteration output string

        Notes
        -----
        Whitespace will be temporarily appended to start and of string.

        Raises
        ------
        ValueError
            Cannot parse input

        """
        tokens = self.tokenize(input)   # adds initial+final whitespace
        # self._input_tokens = tokens     # <--- tokens are saved here
        self._rule_keys = []
        output = ""
        token_i = 1                     # adjust for initial whitespace

        while token_i < len(tokens)-1:  # adjust for final whitespace
            rule_key = self.match_at(token_i, tokens)
            if rule_key is None:
                logger.warning(
                    "No matching transliteration rule at token pos %s of %s"
                    % (token_i, tokens)
                )
                # No parsing rule was found at this location
                if self.ignore_exceptions:
                    token_i += 1
                    continue
                else:
                    raise NoMatchingTransliterationRule
            self._rule_keys.append(rule_key)
            rule = self.rules[rule_key]
            tokens_matched = rule.tokens
            if self._onmatch_rules:
                curr_match_rules = None
                prev_t = tokens[token_i-1]
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
                            token_i-len(onmatch.prev_classes),
                            onmatch.prev_classes,  # double checks last value
                            tokens,
                            check_prev=True, check_next=False, by_class=True
                        ) and self._match_tokens(
                            token_i,
                            onmatch.next_classes,  # double checks first value
                            tokens,
                            check_prev=False, check_next=True, by_class=True
                        ):
                            output += onmatch.production
                            break  # only match best onmatch rule
            output += rule.production
            token_i += len(tokens_matched)
        return output

    def tokenize(self, input):
        """
        Tokenizes an input string.

        Adds initial and trailing whitespace, and consolidates if requested.

        Parameters
        ----------
        input : str
            String to tokenize

        Returns
        -------
        list or None

        Raises
        ------
        ValueError
            Unrecognizable input, such as a character that is not in a token

        Examples
        --------
        >>> from graphtransliterator import GraphTransliterator
        >>> t = {'ab': ['class_ab'], ' ': ['wb']}
        >>> w = {'default': ' ', 'token_class': 'wb', 'consolidate': True}
        >>> r = {'ab': 'AB', ' ': '_'}
        >>> settings = {'tokens': t, 'rules': r, 'whitespace': w}
        >>> gt = GraphTransliterator.from_dict(settings)
        >>> gt.tokenize('ab ')
        ['ab', ' ']

        """
        def is_whitespace(token):
            """Check if token is whitespace."""
            return self.whitespace.token_class in self.tokens[token]

        def match_generator():
            """Generate matches."""
            match = self._tokenizer.match(input, 0)
            while match:
                yield match
                match = self._tokenizer.match(input, match.end())

        # start with a whitespace token
        tokens = [self.whitespace.default]

        matches = match_generator()
        prev_whitespace = True

        match_at = 0
        while match_at < len(input):
            for match in matches:
                match_at = match.end()
                token = match.group(0)
    #           Could save match loc here:
    #           matched_at = match.span(0)[0]
                if is_whitespace(token):
                    if prev_whitespace and self.whitespace.consolidate:
                        continue
                    else:
                        prev_whitespace = True
                else:
                    prev_whitespace = False
                tokens.append(token)

            if match_at != len(input):
                logger.warning(
                    "Unrecognizable token %s at pos %s of %s" % (
                        input[match_at], match_at, input
                    )
                )
                if not self.ignore_exceptions:
                    raise UnrecognizableInputToken
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
        Ruel transliteration rules with specific output productions.

        Parameters
        ----------
        productions : list of str
            list of productions to remove

        Returns
        -------
        GraphTransliterator
            Graph transliterator pruned of certain productions.

        Notes
        -----
        Uses original initialization values to construct a new
        GraphTransliterator, which have no setter, but passes current
        `ignore_exceptions` state.

        """
        __init_parameters__ = self.__init_parameters__
        pruned_rules = [_ for _ in __init_parameters__['rules']
                        if not _['production'] in productions]
        return GraphTransliterator(
            __init_parameters__['tokens'],
            pruned_rules,
            __init_parameters__['onmatch_rules'],
            __init_parameters__['whitespace'],
            __init_parameters__['metadata'],
            ignore_exceptions=self.ignore_exceptions
        )

    @property
    def productions(self):
        """:obj:`list(str)`: List of all possible productions."""
        return [_.production for _ in self._rules]

    @property
    def tokens(self):
        """:obj:`dict` of (:obj:`str`:, :obj:`list` of :obj:`str`): Mappings
        of tokens to a list of classes."""
        return self._tokens

    @property
    def rules(self):
        """:obj:`list` of :obj:`TransliterationRule`: Transliteration rules
        sorted by cost."""
        return self._rules

    @property
    def onmatch_rules(self):
        """:obj:`list` of :obj:`OnMatchRules`: On match rules."""
        return self._onmatch_rules

    @property
    def whitespace(self):
        """:obj:`dict`: Whitespace rules for this transliterator."""
        return self._whitespace

    @classmethod
    def from_dict(cls, settings, **kwargs):
        """
        Construct GraphTransliterator from a dictionary of raw settings.
        This method is used to process YAML and other serialized forms. It
        converts each rule into a `TransliterationRule`, sorted by weight, and
        each `onmatch_rule`.


        Parameters
        ----------
        settings : dict
            Dictionary containing `tokens`, `rules`, `onmatch_rules`
            (optional), `whitespace`, and `metadata` (optional) settings
        """

        validate_raw_settings(settings)
        settings = _process_settings(settings)

        return GraphTransliterator(
            settings['tokens'], settings['rules'], settings['onmatch_rules'],
            settings['whitespace'], settings['metadata'], **kwargs
        )

    @classmethod
    def from_yaml(cls, yaml_str, charnames_escaped=True, **kwargs):
        """
        Construct GraphTransliterator from a YAML str.

        Calls `from_dict`.

        Parameters
        ----------
        yaml_str : str
            YAML mappings of tokens, rules, and (optionally) onmatch_rules
        charnames_escaped : boolean
            Unescape Unicode during YAML read (default True)

        See Also
        --------
        graphtransliterator.GraphTransliterator.from_yaml_file()
        graphtransliterator.GraphTransliterator.from_dict()

        """
        if charnames_escaped:
            yaml_str = _unescape_charnames(yaml_str)

        settings = yaml.safe_load(yaml_str)

        return cls.from_dict(settings, **kwargs)

    @classmethod
    def from_yaml_file(cls, yaml_filename, **kwargs):
        """
        Construct GraphTransliterator from YAML file yaml_filename.

        Calls `from_yaml`.

        Parameters
        ----------
        yaml_filename : str
            Name of YAML file, containing tokens, rules, and (optionally)
            onmatch_rules

        See Also
        --------
        graphtransliterator.GraphTransliterator.from_yaml
        graphtransliterator.GraphTransliterator.from_dict

        """
        with open(yaml_filename, 'r') as f:
            yaml_string = f.read()

        return cls.from_yaml(yaml_string, **kwargs)

    def serialize(self):
        """
        Serialize all relevant settings of Graph Transliterator.

        This is used to allow the GraphTransliterator to be used in Javascript,
        for example.

        Returns
        -------
        dict
        """
        return {
            '_graph': self._graph.to_dict(),
            '_tokens': {token: list(classes)
                        for token, classes in self._tokens.items()},
            '_rules': self._rules,
            '_onmatch_rules': self._onmatch_rules,
            '_onmatch_rules_lookup': self._onmatch_rules_lookup,
            '_whitespace': self._whitespace,
            '_tokenizer_pattern': self._tokenizer.pattern
        }


# ---------- methods ----------


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

    >>> from graphtransliterator import GraphTransliterator
    >>> GraphTransliterator.unescape_charnames(r"H\N{LATIN SMALL LETTER I}")
    'Hi'
    """

    def get_unicode_char(matchobj):
        """Get Unicode character value from escaped character sequences."""
        charname = matchobj.group(0)
        match = re.match(r'\\N{([A-Z ]+)}', charname)
        char = unicodedata.lookup(match.group(1))  # KeyError if invalid
        return char

    return re.sub(r'\\N{[A-Z ]+}', get_unicode_char, input_str)
