# -*- coding: utf-8 -*-

"""
GraphTransliterator core classes.
"""

import json
import logging
import re
from collections import deque
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple, Union, cast

import yaml
from marshmallow import (
    ValidationError,
)

from graphtransliterator import __version__ as __version__

from .ambiguity import check_for_ambiguity
from .exceptions import (
    IncompleteOnMatchRulesCoverageException,
    NoMatchingTransliterationRuleException,
    UnrecognizableInputTokenException,
)
from .graphs import DirectedGraph, VisitLoggingDirectedGraph, VisitLoggingList
from .initialize import (
    _graph_from,
    _onmatch_rules_lookup,
    _tokenizer_pattern_from,
    _tokens_by_class_of,
    _transliteration_rule_of,
    _unescape_charnames,
)
from .process import EasyReadingInput, ProcessedSettingsDict, _process_easyreading_settings
from .schemas import (
    EasyReadingSettingsSchema,
    GraphTransliteratorSchema,
    SettingsSchema,
)
from .types import (
    EasyReadingDict,
    GTEdgeDataType,
    GTNodeDataType,
    GTNodeType,
    NodeId,
    OnMatchRule,
    RawRuleDict,
    Token,
    TokenClass,
    TransliterationRule,
    WhitespaceRule,
)

logger = logging.getLogger("graphtransliterator")
fields_to_dump = ("tokens", "rules", "metadata", "onmatch_rules", "whitespace")


# class GraphTransliteratorSchema(Schema):
#     """Schema for Graph Transliterator."""

#     tokens = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)
#     rules = fields.Nested(TransliterationRuleSchema, many=True, required=True)
#     whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
#     onmatch_rules = fields.Nested(OnMatchRuleSchema, many=True, required=False, allow_none=True)
#     metadata = fields.Dict(
#         keys=fields.Str(),
#         required=False,
#     )
#     ignore_errors = fields.Bool(required=False)
#     onmatch_rules_lookup = fields.Dict(required=False, allow_none=True)
#     tokens_by_class = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=False)
#     graph = fields.Nested(DirectedGraphSchema, many=False, allow_none=True, required=False)
#     tokenizer_pattern = fields.Str(required=False)
#     graphtransliterator_version = fields.Str(required=False)
#     check_ambiguity = fields.Bool(required=False)
#     coverage = fields.Bool(required=False)

#     @pre_load
#     def check_version(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
#         """Raises error if serialized GraphTransliterator is from a later version."""
#         version = data.get("graphtransliterator_version")
#         if version and version > __version__:
#             raise IncorrectVersionException
#         return data

#     @post_load
#     def make_GraphTransliterator(self, data: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
#         for key in ("tokens", "tokens_by_class"):
#             if data.get(key):
#                 data[key] = {k: set(v) for k, v in data[key].items()}
#         if "check_ambiguity" not in data:
#             data["check_ambiguity"] = kwargs.get("check_ambiguity", kwargs.get("check_for_ambiguity", False))
#         return GraphTransliterator(**data)

#     @validates_schema
#     def validate_onmatch_rules_lookup(self, data: Dict[str, Any], **kwargs: Any) -> None:
#         """Check that if there are onmatch_rules_lookup there are onmatch_rules."""
#         if data.get("onmatch_rules_lookup") and not data.get("onmatch_rules"):
#             raise ValidationError("Contains onmatch_rules_lookup but not onmatch_rules.")


class GraphTransliterator:
    _tokens: Dict[str, Set[str]]
    _rules: List[TransliterationRule]
    _tokens_by_class: Dict[str, Set[str]]
    _check_ambiguity: bool
    _whitespace: WhitespaceRule
    _onmatch_rules: Optional[Union[List[OnMatchRule], VisitLoggingList[Any]]]
    _onmatch_rules_lookup: Optional[Dict[str, Dict[str, List[int]]]]
    _metadata: Optional[Dict[str, Any]]
    _ignore_errors: bool
    _tokenizer_pattern: str
    _tokenizer: re.Pattern
    _graph: DirectedGraph[GTNodeType, GTNodeDataType, GTEdgeDataType]
    _rule_keys: List[int]
    _graphtransliterator_version: str
    _input_tokens: List[str]

    def __init__(
        self,
        tokens: Mapping[str, Union[List[str], Set[str]]],
        rules: List[TransliterationRule],
        whitespace: WhitespaceRule,
        onmatch_rules: Optional[Union[List[OnMatchRule], VisitLoggingList[Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ignore_errors: bool = False,
        check_ambiguity: bool = False,
        onmatch_rules_lookup: Optional[Dict[str, Dict[str, List[int]]]] = None,
        tokens_by_class: Optional[Dict[str, Set[str]]] = None,
        graph: Optional[DirectedGraph[GTNodeType, GTNodeDataType, GTEdgeDataType]] = None,
        tokenizer_pattern: Optional[str] = None,
        graphtransliterator_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._tokens = {k: set(v) for k, v in tokens.items()}
        self._rules = [_transliteration_rule_of(r) for r in rules]

        self._tokens_by_class = tokens_by_class or _tokens_by_class_of(
            cast(Dict[str, Union[List[str], Set[str]]], self._tokens)
        )
        self._check_ambiguity = check_ambiguity or kwargs.get("check_for_ambiguity", False)
        if self._check_ambiguity:
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
                    cast(List[OnMatchRule], raw_onmatch),
                )
        else:
            self._onmatch_rules = None
            self._onmatch_rules_lookup = None

        self._metadata = metadata
        self._ignore_errors = ignore_errors or kwargs.get("ignore_errors", False)

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
        obj = super().__new__(cls)
        if "ignore_errors" in kwargs:
            obj._ignore_errors = kwargs["ignore_errors"]
        return obj

    def _match_constraints(
        self,
        rule: TransliterationRule,
        token_i: int,
        t_idx: int,
        tokens: List[str],
    ) -> bool:
        prev_tokens = rule.get("prev_tokens")
        if prev_tokens:
            start_at = token_i - len(prev_tokens)
            if not self._match_tokens(start_at, prev_tokens, tokens, check_prev=True, check_next=False, by_class=False):
                return False

        next_tokens = rule.get("next_tokens")
        if next_tokens:
            if not self._match_tokens(t_idx, next_tokens, tokens, check_prev=False, check_next=True, by_class=False):
                return False

        prev_classes = rule.get("prev_classes")
        if prev_classes:
            start_at = token_i - (len(prev_tokens) if prev_tokens else 0) - len(prev_classes)
            if not self._match_tokens(start_at, prev_classes, tokens, check_prev=True, check_next=False, by_class=True):
                return False

        next_classes = rule.get("next_classes")
        if next_classes:
            offset = len(next_tokens) if next_tokens else 0
            start_at = t_idx + offset
            if not self._match_tokens(start_at, next_classes, tokens, check_prev=False, check_next=True, by_class=True):
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
        if not by_class:
            return tokens[start_i : start_i + len(constraint_values)] == constraint_values

        for i, class_name in enumerate(constraint_values):
            if class_name not in self._tokens[tokens[start_i + i]]:
                return False
        return True

    @property
    def graph(self) -> DirectedGraph[GTNodeType, GTNodeDataType, GTEdgeDataType]:
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
        return [self._rules[_]["tokens"] for _ in self._rule_keys]

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
        return [_.get("production", "") for _ in self.rules]

    @property
    def rules(self) -> List[TransliterationRule]:
        return self._rules

    @property
    def tokens(self) -> Dict[str, Set[str]]:
        return self._tokens

    @property
    def whitespace(self) -> WhitespaceRule:
        return self._whitespace

    def dump(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], GraphTransliteratorSchema(only=fields_to_dump).dump(self))

    def dumps(self) -> str:
        return cast(
            str,
            GraphTransliteratorSchema(only=fields_to_dump).dumps(self),
        )

    def match_at(self, token_i: int, tokens: List[str], match_all: bool = False) -> Union[Optional[int], List[int]]:
        graph = self._graph
        matches: List[int] = []
        stack: deque[Tuple[NodeId, int]] = deque()

        is_coverage = isinstance(graph, VisitLoggingDirectedGraph)

        def _append_children(parent_id: NodeId, t_idx: int) -> None:
            # Cast graph node retrieval to Dict[str, Any] so Mypy recognizes dict operations
            parent_node = cast(Optional[Dict[str, Any]], graph.get_node(parent_id))
            if not parent_node:
                return

            ordered_children: Dict[str, List[int]] = parent_node.get("ordered_children", {})

            rule_child_ids = ordered_children.get("__rules__", [])
            for child_id in reversed(rule_child_ids):
                if is_coverage:
                    cast(VisitLoggingDirectedGraph, graph).visit_edge(parent_id, child_id)
                    cast(VisitLoggingDirectedGraph, graph).visit_node(child_id)
                stack.appendleft((child_id, t_idx))

            if t_idx < len(tokens):
                curr_token = tokens[t_idx]
                if curr_token in ordered_children:
                    token_child_ids = ordered_children[curr_token]
                    for child_id in reversed(token_child_ids):
                        child_node = cast(Optional[Dict[str, Any]], graph.get_node(child_id))
                        if child_node and child_node.get("type") == "Token":
                            if is_coverage:
                                cast(VisitLoggingDirectedGraph, graph).visit_edge(parent_id, child_id)
                                cast(VisitLoggingDirectedGraph, graph).visit_node(child_id)
                            stack.appendleft((child_id, t_idx + 1))

        if is_coverage:
            cast(VisitLoggingDirectedGraph, graph).visit_node(0)

        _append_children(0, token_i)

        while stack:
            node_id, t_idx = stack.popleft()

            # Explicitly cast node to Dict[str, Any]
            curr_node = cast(Optional[Dict[str, Any]], graph.get_node(node_id))

            assert curr_node is not None, "Missing curr_node"

            if curr_node.get("type") == "Rule" and curr_node.get("accepting"):
                # Cast rule_id explicitly to int
                rule_id = cast(int, curr_node.get("rule_key"))

                rule = self.rules[rule_id]

                if self._match_constraints(rule, token_i, t_idx, tokens):
                    if match_all:
                        matches.append(rule_id)
                        continue
                    else:
                        return rule_id
            else:
                _append_children(node_id, t_idx)

        return matches if match_all else None

    def pruned_of(self, productions: Union[str, List[str]]) -> "GraphTransliterator":
        prod_set = {productions} if isinstance(productions, str) else set(productions)
        pruned_rules = [_ for _ in self._rules if _["production"] not in prod_set]
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
            return self.whitespace["token_class"] in self.tokens[tok]

        tokens = [self.whitespace["default"]]
        prev_whitespace = True
        match_at = 0

        while match_at < len(input_):
            match = self._tokenizer.match(input_, match_at)
            if match:
                match_at = match.end()
                token = match.group(0)
                if is_whitespace(token):
                    if prev_whitespace and self.whitespace["consolidate"]:
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

        if self.whitespace["consolidate"]:
            while len(tokens) > 1 and is_whitespace(tokens[-1]):
                tokens.pop()

        tokens.append(self.whitespace["default"])
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
        output_chunks: List[str] = []
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
            tokens_matched = rule["tokens"]
            onmatch_rules_obj = self._onmatch_rules
            if onmatch_rules_obj and self._onmatch_rules_lookup:
                curr_match_rules = None
                prev_t = tokens[token_i - 1]
                curr_t = tokens[token_i]
                curr_t_rules = self._onmatch_rules_lookup.get(curr_t)
                if curr_t_rules:
                    curr_match_rules = curr_t_rules.get(prev_t)
                if curr_match_rules:
                    for onmatch_i in curr_match_rules:
                        raw_onmatch = (
                            onmatch_rules_obj.data[onmatch_i]
                            if isinstance(onmatch_rules_obj, VisitLoggingList)
                            else onmatch_rules_obj[onmatch_i]
                        )
                        onmatch = cast(OnMatchRule, raw_onmatch)
                        if self._match_tokens(
                            token_i - len(onmatch["prev_classes"]),
                            onmatch["prev_classes"],
                            tokens,
                            check_prev=True,
                            check_next=False,
                            by_class=True,
                        ) and self._match_tokens(
                            token_i,
                            onmatch["next_classes"],
                            tokens,
                            check_prev=False,
                            check_next=True,
                            by_class=True,
                        ):
                            if isinstance(onmatch_rules_obj, VisitLoggingList):
                                onmatch_rules_obj.visit(onmatch_i)
                            output_chunks.append(onmatch["production"])
                            break
            output_chunks.append(rule["production"])
            token_i += len(tokens_matched)

        return "".join(output_chunks), matches

    @staticmethod
    def from_dict(dict_settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        check_ambiguity = kwargs.get("check_ambiguity", kwargs.get("check_for_ambiguity", False))
        ignore_errors = kwargs.get("ignore_errors", False)
        coverage = kwargs.get("coverage", False)

        cls_to_instantiate = CoverageTransliterator if coverage else GraphTransliterator

        if "tokens" in dict_settings and "rules" in dict_settings and "whitespace" in dict_settings:
            rules = dict_settings.get("rules")
            if isinstance(rules, list) and len(rules) > 0:
                first_rule = rules[0]
                if isinstance(first_rule, dict) and "production" in first_rule and "tokens" in first_rule:
                    loaded_gt = cast("GraphTransliterator", GraphTransliteratorSchema().load(dict_settings))
                    if ignore_errors:
                        loaded_gt.ignore_errors = True
                    if check_ambiguity:
                        check_for_ambiguity(loaded_gt)
                    if coverage and not isinstance(loaded_gt, CoverageTransliterator):
                        return CoverageTransliterator(
                            tokens=loaded_gt.tokens,
                            rules=loaded_gt.rules,
                            whitespace=loaded_gt.whitespace,
                            onmatch_rules=loaded_gt.onmatch_rules,
                            metadata=loaded_gt.metadata,
                            ignore_errors=loaded_gt.ignore_errors,
                            check_ambiguity=loaded_gt._check_ambiguity,
                        )
                    return loaded_gt

        settings = cast(Dict[str, Any], SettingsSchema().load(dict_settings))

        # Check default whitespace token validity
        ws_default = settings["whitespace"]["default"]
        if ws_default not in settings["tokens"]:
            raise ValidationError(f"Default whitespace token '{ws_default}' is not in tokens.")

        args = [settings["tokens"], settings["rules"], settings["whitespace"]]

        kw = {
            "onmatch_rules": settings.get("onmatch_rules"),
            "metadata": settings.get("metadata"),
            "tokens_by_class": settings.get("tokens_by_class"),
            "graph": settings.get("graph"),
            "tokenizer_pattern": settings.get("tokenizer_pattern"),
            "ignore_errors": ignore_errors,
            "check_ambiguity": check_ambiguity,
        }
        return cls_to_instantiate(*args, **kw)

    @staticmethod
    def from_easyreading_dict(easyreading_settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        loaded = cast(Dict[str, Any], EasyReadingSettingsSchema().load(easyreading_settings))
        processed: ProcessedSettingsDict = _process_easyreading_settings(cast(EasyReadingInput, loaded))
        return GraphTransliterator.from_dict(cast(Dict[str, Any], processed), **kwargs)

    @staticmethod
    def from_yaml(yaml_str: str, charnames_escaped: bool = True, **kwargs: Any) -> "GraphTransliterator":
        if charnames_escaped:
            yaml_str = _unescape_charnames(yaml_str)
        settings = yaml.safe_load(yaml_str)
        return GraphTransliterator.from_easyreading_dict(settings, **kwargs)

    @staticmethod
    def from_yaml_file(yaml_filename: str, **kwargs: Any) -> "GraphTransliterator":
        with open(yaml_filename, "r", encoding="utf-8") as f:
            yaml_string = f.read()
        return GraphTransliterator.from_yaml(yaml_string, **kwargs)

    @staticmethod
    def from_json(json_str: str, **kwargs: Any) -> "GraphTransliterator":
        """Load a GraphTransliterator from a JSON string."""
        data = json.loads(json_str)
        return GraphTransliterator.from_dict(data, **kwargs)

    @staticmethod
    def from_json_file(json_filename: str, **kwargs: Any) -> "GraphTransliterator":
        """Load a GraphTransliterator from a JSON file."""
        with open(json_filename, "r", encoding="utf-8") as f:
            return GraphTransliterator.from_json(f.read(), **kwargs)

    @staticmethod
    def from_dict_file(dict_filename: str, **kwargs: Any) -> "GraphTransliterator":
        """Alias or file loader for dictionary/json files."""
        return GraphTransliterator.from_json_file(dict_filename, **kwargs)

    @staticmethod
    def load(settings: Dict[str, Any], **kwargs: Any) -> "GraphTransliterator":
        return GraphTransliterator.from_dict(settings, **kwargs)

    @staticmethod
    def loads(settings: str, **kwargs: Any) -> "GraphTransliterator":
        _settings = json.loads(settings)
        return GraphTransliterator.from_dict(_settings, **kwargs)

    def merge(self, other: "GraphTransliterator") -> "GraphTransliterator":
        """Merges another GraphTransliterator context cleanly into this one."""
        if (
            self.whitespace["consolidate"] != other.whitespace["consolidate"]
            or self.whitespace["default"] != other.whitespace["default"]
            or self.whitespace["token_class"] != other.whitespace["token_class"]
        ):
            raise ValueError("Configuration Mismatch: The whitespace configurations must be identical to merge.")

        unified_tokens = {k: set(v) for k, v in self.tokens.items()}
        for k, v in other.tokens.items():
            if k in unified_tokens:
                unified_tokens[k].update(v)
            else:
                unified_tokens[k] = set(v)

        unified_rules = list(self.rules) + list(other.rules)

        unified_metadata = {}
        if self.metadata:
            unified_metadata.update(self.metadata)
        if other.metadata:
            unified_metadata.update(other.metadata)

        unified_onmatch = None
        if self.onmatch_rules or other.onmatch_rules:
            unified_onmatch = []
            if self.onmatch_rules:
                unified_onmatch.extend(self.onmatch_rules)
            if other.onmatch_rules:
                unified_onmatch.extend(other.onmatch_rules)

        return GraphTransliterator(
            tokens=unified_tokens,
            rules=unified_rules,
            whitespace=self.whitespace,
            onmatch_rules=unified_onmatch,
            metadata=unified_metadata if unified_metadata else None,
            ignore_errors=self.ignore_errors,
            check_ambiguity=self._check_ambiguity,
        )

    @property
    def settings(self) -> Dict[str, Any]:
        """Returns the structural dictionary of current state matching SettingsSchema."""
        return {
            "tokens": {k: list(v) for k, v in self.tokens.items()},
            "rules": [
                {
                    "tokens": rule["tokens"],
                    "production": rule["production"],
                }
                for rule in self.rules
            ],
            "whitespace": {
                "default": self.whitespace["default"],
                "token_class": self.whitespace["token_class"],
                "consolidate": self.whitespace["consolidate"],
            },
            "metadata": self.metadata,
        }

    @staticmethod
    def merge_easyreading_configs(config1: EasyReadingDict, config2: EasyReadingDict) -> EasyReadingDict:
        """Combines two raw Easy Reading configurations together."""
        w1 = config1["whitespace"]
        w2 = config2["whitespace"]

        if (
            w1.get("consolidate") != w2.get("consolidate")
            or w1.get("default") != w2.get("default")
            or w1.get("token_class") != w2.get("token_class")
        ):
            raise ValueError(
                "Configuration Mismatch: The whitespace settings in both easy reading profiles must match exactly to merge."
            )

        merged_tokens: Dict[Token, List[TokenClass]] = {}
        for token, classes in config1["tokens"].items():
            merged_tokens[token] = list(classes)
        for token, classes in config2["tokens"].items():
            if token in merged_tokens:
                merged_tokens[token] = list(set(merged_tokens[token] + classes))
            else:
                merged_tokens[token] = list(classes)

        merged_rules: Dict[str, str] = dict(config1["rules"])
        merged_rules.update(config2["rules"])

        result: EasyReadingDict = {
            "tokens": merged_tokens,
            "rules": merged_rules,
            "whitespace": {
                "default": w1["default"],
                "token_class": w1["token_class"],
                "consolidate": w1["consolidate"],
            },
        }

        onmatch1 = config1.get("onmatch_rules", [])
        onmatch2 = config2.get("onmatch_rules", [])
        if onmatch1 or onmatch2:
            merged_onmatch: List[Dict[str, str]] = []
            seen_onmatch = []
            for item in onmatch1 + onmatch2:
                if item not in seen_onmatch:
                    seen_onmatch.append(item)
                    merged_onmatch.append(dict(item))
            result["onmatch_rules"] = merged_onmatch

        meta1 = config1.get("metadata", {})
        meta2 = config2.get("metadata", {})
        if meta1 or meta2:
            merged_metadata: Dict[str, Any] = {}
            if meta1:
                merged_metadata.update(meta1)
            if meta2:
                merged_metadata.update(meta2)
            result["metadata"] = merged_metadata

        return result

    def __add__(self, other: "GraphTransliterator") -> "GraphTransliterator":
        if not isinstance(other, GraphTransliterator):
            return NotImplemented
        return self.merge(other)

    def inject_subgraph(
        self, other: "GraphTransliterator", prefix_tokens: Optional[List[str]] = None
    ) -> "GraphTransliterator":
        """Injects another GraphTransliterator's ruleset as a subgraph extension."""
        if (
            self.whitespace["consolidate"] != other.whitespace["consolidate"]
            or self.whitespace["default"] != other.whitespace["default"]
            or self.whitespace["token_class"] != other.whitespace["token_class"]
        ):
            raise ValueError(
                "Graph Injection Mismatch: The whitespace settings of the injected subgraph must match the base configuration exactly."
            )

        merged_tokens = {k: set(v) for k, v in self.tokens.items()}
        for k, v in other.tokens.items():
            if k in merged_tokens:
                merged_tokens[k].update(v)
            else:
                merged_tokens[k] = set(v)

        merged_rules = list(self.rules)

        for rule in other.rules:
            if prefix_tokens:
                new_prev_tokens = prefix_tokens + (rule.get("prev_tokens") or [])
                raw_rule_dict = {
                    "production": rule["production"],
                    "prev_classes": rule.get("prev_classes"),
                    "prev_tokens": new_prev_tokens,
                    "tokens": rule["tokens"],
                    "next_tokens": rule.get("next_tokens"),
                    "next_classes": rule.get("next_classes"),
                }

                from .initialize import _transliteration_rule_of

                merged_rules.append(_transliteration_rule_of(cast(RawRuleDict, raw_rule_dict)))
            else:
                merged_rules.append(rule)

        merged_onmatch = None
        if self.onmatch_rules or other.onmatch_rules:
            merged_onmatch = []
            if self.onmatch_rules:
                merged_onmatch.extend(self.onmatch_rules)
            if other.onmatch_rules:
                for o_rule in other.onmatch_rules:
                    if o_rule not in merged_onmatch:
                        merged_onmatch.append(o_rule)

        merged_metadata = {}
        if self.metadata:
            merged_metadata.update(self.metadata)
        if other.metadata:
            merged_metadata.update(other.metadata)

        return GraphTransliterator(
            tokens=merged_tokens,
            rules=merged_rules,
            whitespace=self.whitespace,
            onmatch_rules=merged_onmatch if merged_onmatch else None,
            metadata=merged_metadata if merged_metadata else None,
            ignore_errors=self.ignore_errors,
            check_ambiguity=self._check_ambiguity,
        )

    def __rshift__(self, other: "GraphTransliterator") -> "GraphTransliterator":
        if not isinstance(other, GraphTransliterator):
            return NotImplemented
        return self.inject_subgraph(other)


class CoverageTransliterator(GraphTransliterator):
    """Subclass of GraphTransliterator logging graph and onmatch rule traversal."""

    _graph: VisitLoggingDirectedGraph
    _onmatch_rules: Optional[VisitLoggingList[Any]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        GraphTransliterator.__init__(self, *args, **kwargs)
        self._graph = VisitLoggingDirectedGraph(self._graph)
        if self._onmatch_rules is not None:
            self._onmatch_rules = cast(Any, VisitLoggingList(self._onmatch_rules))

    def clear_visited(self) -> None:
        self._graph.clear_visited()
        if self._onmatch_rules:
            self._onmatch_rules.clear_visited()

    def check_onmatchrules_coverage(self, raise_exception: bool = True) -> bool:
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
        return self._graph.check_coverage(raise_exception=raise_exception) and self.check_onmatchrules_coverage(
            raise_exception=raise_exception
        )
