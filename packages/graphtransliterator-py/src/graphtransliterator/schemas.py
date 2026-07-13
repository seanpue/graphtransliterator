# -*- coding: utf-8 -*-

from marshmallow import (
    fields,
    post_load,
    pre_dump,
    Schema,
    validate,
    ValidationError,
    validates_schema,
)

from collections import defaultdict
from typing import Any, Union, cast
from typing_extensions import TypedDict  # Clear import for TypedDict
from .graphs import DirectedGraph
from .rules import TransliterationRule, WhitespaceRules, OnMatchRule
from .types import NodeData, LoadedGraphDict
from .initialize import (
    _onmatch_rule_of,
    _transliteration_rule_of,
    _whitespace_rules_of,
    RawRuleDict,
    RawOnMatchDict,
    RawWhitespaceDict,
)
from .process import RULE_RE, ONMATCH_RE
import copy


# Defined here to prevent circular loops in types.py
class LoadedSettingsDict(TypedDict):
    tokens: dict[str, Union[list[str], set[str]]]
    rules: list[TransliterationRule]
    whitespace: WhitespaceRules
    metadata: dict[str, Any]
    onmatch_rules: list[OnMatchRule]


class WhitespaceDictSettingsSchema(Schema):
    """Schema for Whitespace definition as a `dict`."""

    default = fields.Str(required=True)
    token_class = fields.Str(required=True)
    consolidate = fields.Boolean(required=True)


class WhitespaceSettingsSchema(WhitespaceDictSettingsSchema):
    """Schema for Whitespace definition that loads as :class:`WhitespaceRules.`"""

    @post_load
    def make_whitespace_rules(self, data: RawWhitespaceDict, **kwargs: Any) -> WhitespaceRules:
        return _whitespace_rules_of(data)


class EasyReadingSettingsSchema(Schema):
    """Schema for easy reading settings.

    Provides initial validation based on easy reading format.
    """

    tokens = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)
    rules = fields.Dict(
        keys=fields.Str(validate=validate.Regexp(RULE_RE)),
        values=fields.Str(),
        required=True,
    )
    onmatch_rules = fields.List(
        fields.Dict(
            keys=fields.Str(validate=validate.Regexp(ONMATCH_RE)),
            values=fields.Str(),
            required=False,
        )
    )
    metadata = fields.Dict(
        keys=fields.Str(),
        # no restriction on values
        required=False,
    )
    whitespace = fields.Nested(WhitespaceDictSettingsSchema)


class TransliterationRuleSchema(Schema):
    """Schema for :class:`TransliterationRule`."""

    production = fields.Str(required=True)
    tokens = fields.List(fields.Str(), required=True)
    prev_classes = fields.List(fields.Str(), allow_none=True)
    next_classes = fields.List(fields.Str(), allow_none=True)
    prev_tokens = fields.List(fields.Str(), allow_none=True)
    next_tokens = fields.List(fields.Str(), allow_none=True)

    class Meta:
        fields = (
            "production",
            "prev_classes",
            "prev_tokens",
            "tokens",
            "next_classes",
            "next_tokens",
            "cost",
        )

    @pre_dump
    def remove_nulls(self, data: TransliterationRule, **kwargs: Any) -> dict[str, Any]:
        """Removes None values from TransliterationRule to compress JSON."""
        return {k: v for k, v in data._asdict().items() if v is not None}

    @post_load
    def make_transliteration_rule(self, data: RawRuleDict, **kwargs: Any) -> TransliterationRule:
        return _transliteration_rule_of(data)


class OnMatchRuleSchema(Schema):
    """Schema for :class:`OnMatchRule`."""

    prev_classes = fields.List(fields.Str())
    next_classes = fields.List(fields.Str())
    production = fields.Str()

    class Meta:
        fields = ("prev_classes", "next_classes", "production")

    @post_load
    def make_onmatch_rule(self, data: RawOnMatchDict, **kwargs: Any) -> OnMatchRule:
        return _onmatch_rule_of(data)


class SettingsSchema(Schema):
    """Schema for settings in dictionary format.

    Performs validation.
    """

    tokens = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)
    rules = fields.Nested(TransliterationRuleSchema, many=True, required=True)
    whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
    metadata = fields.Dict(
        keys=fields.Str(),
        required=False,
    )
    onmatch_rules = fields.Nested(OnMatchRuleSchema, many=True, required=False)

    @post_load
    def sort_rules_by_cost(self, data: LoadedSettingsDict, **kwargs: Any) -> LoadedSettingsDict:
        """Sort rules by cost."""
        data["rules"] = sorted(data["rules"], key=lambda rule: rule.cost)
        return data

    @post_load
    def token_classes_to_sets(self, data: LoadedSettingsDict, **kwargs: Any) -> LoadedSettingsDict:
        data["tokens"] = {k: set(cast(list[str], v)) for k, v in data["tokens"].items()}
        return data

    @validates_schema
    def validate_token_classes(self, data: LoadedSettingsDict, **kwargs: Any) -> None:
        class_errors: dict[str, list[str]] = defaultdict(list)
        token_classes = list(set().union(*data["tokens"].values()))

        for rule_type in ("onmatch_rules", "rules"):
            rules_list = cast(list[Union[TransliterationRule, OnMatchRule]], data.get(rule_type))
            if not rules_list:
                continue
            for rule in rules_list:
                for property_name in ("prev_classes", "next_classes"):
                    values = getattr(rule, property_name)
                    if not values:
                        continue
                    for _ in values:
                        if _ not in token_classes:
                            class_errors[rule_type].append(
                                'Invalid token class "{}" in {} of {}'.format(_, property_name, rule)
                            )

        whitespace = data["whitespace"]
        whitespace_token_class = whitespace.token_class
        if whitespace_token_class not in token_classes:
            class_errors["whitespace"].append(
                'Invalid token class "{}" in whitespace "{}".'.format(whitespace_token_class, whitespace)
            )
        if class_errors:
            raise ValidationError(dict(class_errors))

    @validates_schema
    def validate_tokens(self, data: LoadedSettingsDict, **kwargs: Any) -> None:
        token_errors: dict[str, list[str]] = defaultdict(list)
        token_types = data["tokens"].keys()

        whitespace = data["whitespace"]
        default_whitespace = whitespace.default
        if default_whitespace not in token_types:
            token_errors["whitespace"].append('Invalid default token "{}" in whitespace.'.format(default_whitespace))

        rules = cast(list[TransliterationRule], data.get("rules"))
        if rules:
            for rule in rules:
                for property_name in ("tokens", "prev_tokens", "next_tokens"):
                    values = getattr(rule, property_name)
                    if not values:
                        continue
                    for _ in values:
                        if _ not in token_types:
                            token_errors["rules"].append(
                                'Invalid token "{}" in {} of rule {}'.format(_, property_name, rule)
                            )
        if token_errors:
            raise ValidationError(dict(token_errors))


class ConstraintSchema(Schema):
    prev_classes = fields.List(fields.Str())
    prev_tokens = fields.List(fields.Str())
    next_tokens = fields.List(fields.Str())
    next_classes = fields.List(fields.Str())


class EdgeDataSchema(Schema):
    token = fields.Str()
    cost = fields.Float()
    constraints = fields.Nested(ConstraintSchema)


class NodeDataSchema(Schema):
    token = fields.String()
    type = fields.String()
    ordered_children = fields.Dict()
    accepting = fields.Bool()
    rule_key = fields.Int()

    @pre_dump
    def strip_empty(self, data: NodeData, **kwargs: Any) -> dict[str, Any]:
        """Remove keys with empty values, allowing zero."""
        _data = {k: v for k, v in data.items() if v or (type(v) is int and v == 0)}
        return _data


class DirectedGraphSchema(Schema):
    """Schema for :class:`DirectedGraph`."""

    edge = fields.Dict(
        keys=fields.Int(),
        values=fields.Dict(keys=fields.Int, values=fields.Nested(EdgeDataSchema)),
    )
    node = fields.List(fields.Nested(NodeDataSchema))
    edge_list = fields.List(fields.Tuple((fields.Int(), fields.Int())))

    class Meta:
        fields = ("node", "edge", "edge_list")

    @post_load
    def make_graph(self, data: LoadedGraphDict, **kwargs: Any) -> DirectedGraph:
        _data = copy.deepcopy(data)
        return DirectedGraph(
            node=_data.get("node", []),
            edge=_data.get("edge", {}),
            edge_list=_data.get("edge_list"),
        )

    @pre_dump
    def sort_edge_list(self, data: DirectedGraph, **kwargs: Any) -> dict[str, Any]:
        """Sort edge list to make dumps consistent."""
        return {
            "node": data.node,
            "edge": data.edge,
            "edge_list": sorted(data.edge_list),
        }


class GraphTransliteratorSchema(Schema):
    """Schema for GraphTransliterator."""

    settings = fields.Nested(SettingsSchema, required=True)
    graph = fields.Nested(DirectedGraphSchema, required=True)
