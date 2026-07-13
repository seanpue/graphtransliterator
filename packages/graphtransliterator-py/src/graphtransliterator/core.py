# -*- coding: utf-8 -*-

"""
GraphTransliterator core classes.
"""

from .ambiguity import check_for_ambiguity
from .compression import compress_config, decompress_config
from .exceptions import (
    IncompleteOnMatchRulesCoverageException,
    IncorrectVersionException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)
from .graphs import VisitLoggingDirectedGraph, VisitLoggingList, DirectedGraph, EdgeData
from .rules import TransliterationRule, OnMatchRule, WhitespaceRules
from .initialize import (
    _graph_from,
    _onmatch_rules_lookup,
    _tokenizer_pattern_from,
    _tokens_by_class_of,
    _unescape_charnames,
)
from .process import _process_easyreading_settings, ProcessedSettingsDict
from .schemas import (
    DirectedGraphSchema,
    EasyReadingSettingsSchema,
    OnMatchRuleSchema,
    SettingsSchema,
    TransliterationRuleSchema,
    WhitespaceSettingsSchema,
)
from collections import deque

from graphtransliterator import __version__ as __version__
import json
import logging
from marshmallow import (
    fields,
    pre_load,
    post_load,
    Schema,
    validates_schema,
    ValidationError,
)
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast, Mapping, Iterable
import yaml

logger = logging.getLogger("graphtransliterator")

DEFAULT_COMPRESSION_LEVEL = 2
HIGHEST_COMPRESSION_LEVEL = 2


class GraphTransliteratorSchema(Schema):
    """Schema for Graph Transliterator."""

    tokens = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)
    rules = fields.Nested(TransliterationRuleSchema, many=True, required=True)
    whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
    onmatch_rules = fields.Nested(OnMatchRuleSchema, many=True, required=False, allow_none=True)
    metadata = fields.Dict(
        keys=fields.Str(),
        required=False,
    )
    ignore_errors = fields.Bool(required=False)
    onmatch_rules_lookup = fields.Dict(required=False, allow_none=True)
    tokens_by_class = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=False)
    graph = fields.Nested(DirectedGraphSchema, many=False, allow_none=True, required=False)
    tokenizer_pattern = fields.Str(required=False)
    graphtransliterator_version = fields.Str(required=False)
    check_ambiguity = fields.Bool(required=False)
    coverage = fields.Bool(required=False)

    @pre_load
    def check_version_and_compression(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Raises error if serialized GraphTransliterator is from a later version."""
        version = data.get("graphtransliterator_version")
        if version and version > __version__:
            raise IncorrectVersionException
        compressed_settings = data.get("compressed_settings")
        if compressed_settings:
            data = decompress_config(compressed_settings)
            data.update(graphtransliterator_version=version)
        return data

    @post_load
    def make_GraphTransliterator(self, data: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        for key in ("tokens", "tokens_by_class"):
            if data.get(key):
                data[key] = {k: set(v) for k, v in data[key].items()}
        data["check_ambiguity"] = kwargs.get("check_ambiguity", False)
        return GraphTransliterator(**data)

    @validates_schema
    def validate_onmatch_rules_lookup(self, data: Dict[str, Any], **kwargs: Any) -> None:
        """Check that if there are onmatch_rules_lookup there are onmatch_rules."""
        if data.get("onmatch_rules_lookup") and not data.get("onmatch_rules"):
            raise ValidationError("Contains onmatch_rules_lookup but not onmatch_rules.")


class GraphTransliterator:
    _tokens: Dict[str, Set[str]]
    _rules: List[TransliterationRule]
    _tokens_by_class: Dict[str, Set[str]]
    _check_ambiguity: bool
    _whitespace: WhitespaceRules
    _onmatch_rules: Optional[Union[List[OnMatchRule], VisitLoggingList[Any]]]
    _onmatch_rules_lookup: Optional[Dict[str, Dict[str, List[int]]]]
    _metadata: Optional[Dict[str, Any]]
    _ignore_errors: bool
    _tokenizer_pattern: str
    _tokenizer: re.Pattern
    _graph: DirectedGraph
    _rule_keys: List[int]
    _graphtransliterator_version: str
    _input_tokens: List[str]

    def __init__(
        self,
        tokens: Mapping[str, Union[List[str], Set[str]]],
        rules: List[TransliterationRule],
        whitespace: WhitespaceRules,
        onmatch_rules: Optional[Union[List[OnMatchRule], VisitLoggingList[Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ignore_errors: bool = False,
        check_ambiguity: bool = True,
        onmatch_rules_lookup: Optional[Dict[str, Dict[str, List[int]]]] = None,
        tokens_by_class: Optional[Dict[str, Set[str]]] = None,
        graph: Optional[DirectedGraph] = None,
        tokenizer_pattern: Optional[str] = None,
        graphtransliterator_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._tokens = {k: set(v) for k, v in tokens.items()}
        self._rules = rules
        
        self._tokens_by_class = tokens_by_class or _tokens_by_class_of(
            cast(Dict[str, Union[List[str], Set[str]]], self._tokens)
        )
        self._check_ambiguity = check_ambiguity
        if check_ambiguity:
            check_for_ambiguity(self)
        self._whitespace = whitespace

        if onmatch_rules:
            self._onmatch_rules = onmatch_rules
            if onmatch_rules_lookup:
                self._onmatch_rules_lookup = onmatch_rules_lookup
            else:
                raw_onmatch = onmatch_rules.data if isinstance(onmatch_rules, VisitLoggingList) else onmatch_rules
                self._onmatch_rules_lookup = _onmatch_rules_lookup(
                    cast(Dict[str, Union[List[str], Set[str]]], self._tokens),
                    cast(List[OnMatchRule], raw_onmatch)
                )
        else:
            self._onmatch_rules = None
            self._onmatch_rules_lookup = None

        self._metadata = metadata
        self._ignore_errors = ignore_errors

        if not tokenizer_pattern:
            tokenizer_pattern = _tokenizer_pattern_from(list(tokens.keys()))
        self._tokenizer_pattern = tokenizer_pattern
        self._tokenizer = re.compile(tokenizer_pattern, flags=re.S)

        if not graph:
            graph = _graph_from(rules)
        self._graph = graph

        self._rule_keys = []
        self._input_tokens = []

        if not graphtransliterator_version:
            graphtransliterator_version = __version__
        self._graphtransliterator_version = graphtransliterator_version

    
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Intercept subclass instantiation to filter out CLI parameters like ignore_errors."""
        if not hasattr(cls, "_init_wrapped"):
            orig_init = cls.__init__
            
            import inspect
            def safe_init(self: Any, *inner_args: Any, **inner_kwargs: Any) -> None:
                sig = inspect.signature(orig_init)
                has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                
                filtered_kwargs = {}
                for k, v in inner_kwargs.items():
                    if has_kwargs or k in sig.parameters or k == "self":
                        filtered_kwargs[k] = v
                    elif k == "ignore_errors":
                        setattr(self, "ignore_errors", v)
                        
                orig_init(self, *inner_args, **filtered_kwargs)
                
            setattr(cls, "__init__", safe_init)
            cls._init_wrapped = True
            
        return super().__new__(cls)

    def _match_constraints(self, target_edge: EdgeData, curr_node: Dict[str, Any], token_i: int, tokens: List[str]) -> bool:
        constraints = target_edge.get("constraints")
        rules = self.rules
        if not constraints:
            return True
            
        for c_type, raw_values in constraints.items():
            c_values = cast(List[str], raw_values)
            
            if c_type == "prev_tokens":
                num_tokens = len(rules[curr_node["rule_key"]].tokens)
                start_at = token_i
                start_at -= num_tokens
                start_at -= len(c_values)

                if not self._match_tokens(
                    start_at,
                    c_values,
                    tokens,
                    check_prev=True,
                    check_next=False,
                    by_class=False,
                ):
                    return False
            elif c_type == "next_tokens":
                start_at = token_i

                if not self._match_tokens(
                    start_at,
                    c_values,
                    tokens,
                    check_prev=False,
                    check_next=True,
                    by_class=False,
                ):
                    return False

            elif c_type == "prev_classes":
                num_tokens = len(rules[curr_node["rule_key"]].tokens)
                start_at = token_i
                start_at -= num_tokens
                prev_tokens = constraints.get("prev_tokens")
                if prev_tokens:
                    start_at -= len(cast(List[str], prev_tokens))
                start_at -= len(c_values)
                if not self._match_tokens(
                    start_at,
                    c_values,
                    tokens,
                    check_prev=True,
                    check_next=False,
                    by_class=True,
                ):
                    return False

            elif c_type == "next_classes":
                start_at = token_i
                next_tokens = constraints.get("next_tokens")
                if next_tokens:
                    start_at += len(cast(List[str], next_tokens))
                if not self._match_tokens(
                    start_at,
                    c_values,
                    tokens,
                    check_prev=False,
                    check_next=True,
                    by_class=True,
                ):
                    return False

        return True

    def _match_tokens(
        self,
        start_i: int,
        constraint_values: List[str],
        tokens: List[str],
        check_prev: bool = True,
        check_next: bool = True,
        by_class: bool = False,
    ) -> bool:
        if check_prev and start_i < 0:
            return False
        if check_next and start_i + len(constraint_values) > len(tokens):
            return False
        for i in range(0, len(constraint_values)):
            if by_class:
                if constraint_values[i] not in self._tokens[tokens[start_i + i]]:
                    return False
            elif tokens[start_i + i] != constraint_values[i]:
                return False
        return True

    @property
    def graph(self) -> DirectedGraph:
        return self._graph

    @property
    def graphtransliterator_version(self) -> str:
        return self._graphtransliterator_version

    @property
    def ignore_errors(self) -> bool:
        return self._ignore_errors

    @ignore_errors.setter
    def ignore_errors(self, value: bool) -> None:
        self._ignore_errors = value

    @property
    def last_input_tokens(self) -> List[str]:
        return self._input_tokens

    @property
    def last_matched_rule_tokens(self) -> List[List[str]]:
        return [self._rules[_].tokens for _ in self._rule_keys]

    @property
    def last_matched_rules(self) -> List[TransliterationRule]:
        return [self._rules[_] for _ in self._rule_keys]

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        return self._metadata

    @property
    def onmatch_rules_lookup(self) -> Optional[Dict[str, Dict[str, List[int]]]]:
        return self._onmatch_rules_lookup

    @property
    def tokenizer_pattern(self) -> str:
        return self._tokenizer_pattern

    @property
    def tokens_by_class(self) -> Dict[str, Set[str]]:
        return self._tokens_by_class

    @property
    def onmatch_rules(self) -> Optional[List[OnMatchRule]]:
        if isinstance(self._onmatch_rules, VisitLoggingList):
            return cast(List[OnMatchRule], self._onmatch_rules.data)
        return self._onmatch_rules

    @property
    def productions(self) -> List[str]:
        return [_.production for _ in self.rules]

    @property
    def rules(self) -> List[TransliterationRule]:
        return self._rules

    @property
    def tokens(self) -> Dict[str, Set[str]]:
        return self._tokens

    @property
    def whitespace(self) -> WhitespaceRules:
        return self._whitespace

    def dump(self, compression_level: int = 0) -> Dict[str, Any]:
        if compression_level == 0:
            return cast(Dict[str, Any], GraphTransliteratorSchema().dump(self))
        elif compression_level not in range(1, HIGHEST_COMPRESSION_LEVEL + 1):
            raise ValueError(f"Compression level must be between 0 and {HIGHEST_COMPRESSION_LEVEL}")
        return {
            "graphtransliterator_version": __version__,
            "compressed_settings": compress_config(
                GraphTransliteratorSchema().dump(self),
                compression_level=compression_level,
            ),
        }

    def dumps(self, compression_level: int = 2) -> str:
        if compression_level == 0:
            return cast(str, GraphTransliteratorSchema().dumps(self))
        _config = self.dump(compression_level=compression_level)
        return json.dumps(_config, separators=(",", ":"))

    def match_at(self, token_i: int, tokens: List[str], match_all: bool = False) -> Union[Optional[int], List[int]]:
        graph = self._graph
        graph_node = graph.node
        graph_edge = graph.edge
        matches: List[int] = []
        stack: deque = deque()

        def _append_children(node_key: int, t_idx: int) -> None:
            ordered_children = graph_node[node_key].get("ordered_children")
            if ordered_children:
                children = ordered_children.get(tokens[t_idx])
                if children:
                    for child_key in reversed(children):
                        stack.appendleft((child_key, node_key, t_idx))
                else:
                    rules_keys = ordered_children.get("__rules__")
                    if rules_keys:
                        for rule_key in reversed(rules_keys):
                            stack.appendleft((rule_key, node_key, t_idx))

        _append_children(0, token_i)

        while stack:
            node_key, parent_key, t_idx = stack.popleft()
            curr_node = graph_node[node_key]
            incident_edge = cast(EdgeData, graph_edge[parent_key][node_key])
            
            if curr_node.get("accepting") and self._match_constraints(incident_edge, curr_node, t_idx, tokens):
                if match_all:
                    matches.append(curr_node["rule_key"])
                    continue
                else:
                    return cast(int, curr_node["rule_key"])
            else:
                if t_idx < len(tokens) - 1:
                    t_idx += 1
                _append_children(node_key, t_idx)
                
        return cast(Union[Optional[int], List[int]], matches if match_all else None)

    def pruned_of(self, productions: Union[str, List[str]]) -> "GraphTransliterator":
        prod_set = {productions} if isinstance(productions, str) else set(productions)
        pruned_rules = [_ for _ in self._rules if _.production not in prod_set]
        return GraphTransliterator(
            self._tokens,
            pruned_rules,
            self._whitespace,
            onmatch_rules=self.onmatch_rules,
            metadata=self._metadata,
            ignore_errors=self._ignore_errors,
            check_ambiguity=self._check_ambiguity,
        )

    def tokenize(self, input_: str) -> List[str]:
        def is_whitespace(tok: str) -> bool:
            return self.whitespace.token_class in self.tokens[tok]

        tokens = [self.whitespace.default]
        prev_whitespace = True
        match_at = 0
        
        while match_at < len(input_):
            match = self._tokenizer.match(input_, match_at)
            if match:
                match_at = match.end()
                token = match.group(0)
                if is_whitespace(token):
                    if prev_whitespace and self.whitespace.consolidate:
                        continue
                    else:
                        prev_whitespace = True
                else:
                    prev_whitespace = False
                tokens.append(token)
            else:
                logger.warning("Unrecognizable token %s at pos %s of %s" % (input_[match_at], match_at, input_))
                if not self.ignore_errors:
                    raise UnrecognizableInputTokenException
                else:
                    match_at += 1

        if self.whitespace.consolidate:
            while len(tokens) > 1 and is_whitespace(tokens[-1]):
                tokens.pop()

        tokens.append(self.whitespace.default)
        return tokens

    def transliterate(self, input_: str) -> str:
        output, _ = self._transliterate_core(input_)
        return output

    def transliterate_with_details(self, input_: str) -> Tuple[str, List[TransliterationRule]]:
        return self._transliterate_core(input_)

    def _transliterate_core(self, input_: str) -> Tuple[str, List[TransliterationRule]]:
        tokens = self.tokenize(input_)
        self._input_tokens = tokens
        self._rule_keys = []
        output = ""
        token_i = 1
        matches: List[TransliterationRule] = []

        while token_i < len(tokens) - 1:
            rule_key = cast(Optional[int], self.match_at(token_i, tokens))
            if rule_key is None:
                logger.warning("No matching transliteration rule at token pos %s of %s" % (token_i, tokens))
                if self.ignore_errors:
                    token_i += 1
                    continue
                else:
                    raise NoMatchingTransliterationRuleException
            self._rule_keys.append(rule_key)

            rule = self.rules[rule_key]
            matches.append(rule)
            tokens_matched = rule.tokens
            if self._onmatch_rules and self._onmatch_rules_lookup:
                curr_match_rules = None
                prev_t = tokens[token_i - 1]
                curr_t = tokens[token_i]
                curr_t_rules = self._onmatch_rules_lookup.get(curr_t)
                if curr_t_rules:
                    curr_match_rules = curr_t_rules.get(prev_t)
                if curr_match_rules:
                    for onmatch_i in curr_match_rules:
                        onmatch = (
                            self._onmatch_rules.data[onmatch_i]
                            if isinstance(self._onmatch_rules, VisitLoggingList)
                            else self._onmatch_rules[onmatch_i]
                        )
                        if self._match_tokens(
                            token_i - len(onmatch.prev_classes),
                            onmatch.prev_classes,
                            tokens,
                            check_prev=True,
                            check_next=False,
                            by_class=True,
                        ) and self._match_tokens(
                            token_i,
                            onmatch.next_classes,
                            tokens,
                            check_prev=False,
                            check_next=True,
                            by_class=True,
                        ):
                            output += onmatch.production
                            break
            output += rule.production
            token_i += len(tokens_matched)

        return output, matches

    @staticmethod
    def from_dict(dict_settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        settings = SettingsSchema().load(dict_settings)
        args = [settings["tokens"], settings["rules"], settings["whitespace"]]
        kw = {
            "onmatch_rules": settings.get("onmatch_rules"),
            "metadata": settings.get("metadata"),
            "tokens_by_class": settings.get("tokens_by_class"),
            "graph": settings.get("graph"),
            "tokenizer_pattern": settings.get("tokenizer_pattern"),
            "ignore_errors": kwargs.get("ignore_errors", False),
            "check_ambiguity": kwargs.get("check_ambiguity", True),
        }
        return GraphTransliterator(*args, **kw)

    @staticmethod
    def from_easyreading_dict(easyreading_settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        _ = EasyReadingSettingsSchema().load(easyreading_settings)
        processed: ProcessedSettingsDict = _process_easyreading_settings(_)
        return GraphTransliterator.from_dict(cast(Dict[str, Any], processed), **kwargs)

    @staticmethod
    def from_yaml(yaml_str: str, charnames_escaped: bool = True, **kwargs: Any) -> "GraphTransliterator":
        if charnames_escaped:
            yaml_str = _unescape_charnames(yaml_str)
        settings = yaml.safe_load(yaml_str)
        return GraphTransliterator.from_easyreading_dict(settings, **kwargs)

    @staticmethod
    def from_yaml_file(yaml_filename: str, **kwargs: Any) -> "GraphTransliterator":
        with open(yaml_filename, "r") as f:
            yaml_string = f.read()
        return GraphTransliterator.from_yaml(yaml_string, **kwargs)

    @staticmethod
    def load(settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        return cast("GraphTransliterator", GraphTransliteratorSchema().load(dict(settings, **kwargs)))

    @staticmethod
    def loads(settings: str, **kwargs: Any) -> "GraphTransliterator":
        _settings = dict(json.loads(settings), **kwargs)
        return cast("GraphTransliterator", GraphTransliteratorSchema().load(_settings))


class CoverageTransliterator(GraphTransliterator):
    """Subclass of GraphTransliterator that logs visits to graph and on_match rules."""

    _graph: VisitLoggingDirectedGraph
    _onmatch_rules: Optional[VisitLoggingList[Any]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        GraphTransliterator.__init__(self, *args, **kwargs)
        self._graph = VisitLoggingDirectedGraph(self._graph)
        if self._onmatch_rules is not None:
            self._onmatch_rules = cast(Any, VisitLoggingList(self._onmatch_rules))

    def clear_visited(self) -> None:
        """Clear visited flags from graph and onmatch_rules."""
        self._graph.clear_visited()
        if self._onmatch_rules:
            self._onmatch_rules.clear_visited()

    def check_onmatchrules_coverage(self, raise_exception: bool = True) -> bool:
        """Check coverage of onmatch rules."""
        errors = []
        onmatch_rules = self._onmatch_rules
        if not onmatch_rules:
            return True
        for i, onmatch_rule in enumerate(onmatch_rules.data):
            if i not in onmatch_rules.visited:
                logger.warning("On Match Rule {} [{}] has not been visited.".format(i, onmatch_rule))
                errors.append(i)
        if errors and raise_exception:
            error_msg = "Missed OnMatchRules: " + ",".join([str(i) for i in errors])
            raise IncompleteOnMatchRulesCoverageException(error_msg)
        return not errors

    def check_coverage(self, raise_exception: bool = True) -> bool:
        """Check coverage of graph and onmatch rules."""
        return self._graph.check_coverage(raise_exception=raise_exception) and self.check_onmatchrules_coverage(
            raise_exception=raise_exception
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        orig_init = cls.__init__
        
        import inspect
        def safe_init(self: Any, *args: Any, **inner_kwargs: Any) -> None:
            sig = inspect.signature(orig_init)
            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            
            filtered_kwargs = {}
            extra_kwargs = {}
            for k, v in inner_kwargs.items():
                if has_kwargs or k in sig.parameters or k == "self":
                    filtered_kwargs[k] = v
                else:
                    extra_kwargs[k] = v
            
            orig_init(self, *args, **filtered_kwargs)
            if "ignore_errors" in extra_kwargs:
                self.ignore_errors = extra_kwargs["ignore_errors"]
                
        setattr(cls, "__init__", safe_init)