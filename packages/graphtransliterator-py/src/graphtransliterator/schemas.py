# -*- coding: utf-8 -*-

import copy
import re
from collections import defaultdict
from typing import Any, Iterable, Union, cast

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    validate,
    validates_schema,
)

from .graphs import DirectedGraph
from .initialize import (
    _onmatch_rule_of,
    _whitespace_rules_of,
)
from .process import ONMATCH_RE, RULE_RE
from .types import (
    LoadedGraphDict,
    LoadedSettingsDict,
    OnMatchRule,
    RawOnMatchDict,
    RawWhitespaceDict,
    TransliterationRule,
    WhitespaceRule,
)


class WhitespaceDictSettingsSchema(Schema):
    """Schema for Whitespace definition as a `dict`."""

    default = fields.Str(required=True)
    token_class = fields.Str(required=True)
    consolidate = fields.Boolean(required=True)


class WhitespaceSettingsSchema(WhitespaceDictSettingsSchema):
    """Schema for Whitespace definition that loads as a WhitespaceRule."""

    @post_load
    def make_whitespace_rules(self, data: RawWhitespaceDict, **kwargs: Any) -> WhitespaceRule:
        return _whitespace_rules_of(data)


class EasyReadingSettingsSchema(Schema):
    """Schema for easy reading settings format."""

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
    metadata = fields.Dict(keys=fields.Str(), required=False)
    whitespace = fields.Nested(WhitespaceDictSettingsSchema)

    @validates_schema
    def validate_whitespace(self, data: dict[str, Any], **kwargs: Any) -> None:
        tokens = data.get("tokens", {})
        whitespace = data.get("whitespace", {})

        if not whitespace:
            return

        default_ws = whitespace.get("default")
        token_class_ws = whitespace.get("token_class")

        if default_ws and default_ws not in tokens:
            raise ValidationError(
                f"Default whitespace token '{default_ws}' not found in tokens.",
                field_name="whitespace",
            )

        all_classes = {cls for classes in tokens.values() if isinstance(classes, (list, set, tuple)) for cls in classes}
        if token_class_ws and token_class_ws not in all_classes:
            raise ValidationError(
                f"Whitespace token class '{token_class_ws}' not found in defined token classes.",
                field_name="whitespace",
            )

    @validates_schema
    @validates_schema
    def validate_rules_tokens(self, data: dict[str, Any], **kwargs: Any) -> None:
        """Validate that tokens and token classes specified in easy-reading rules exist in defined tokens."""
        tokens = data.get("tokens", {})
        rules = data.get("rules", {})

        if not rules or not tokens:
            return

        all_tokens = set(tokens.keys())
        all_classes = {cls for classes in tokens.values() if isinstance(classes, (list, set, tuple)) for cls in classes}

        # Match token classes like <class_name>
        class_pattern = re.compile(r"<([^>]+)>")
        # Match tokens (strings outside of <> and stripped of constraint parentheses ())
        token_clean_pattern = re.compile(r"[()<>]")

        for rule_key in rules.keys():
            # 1. Validate Token Classes referenced in rule_key (e.g., <class_nonexisting>)
            referenced_classes = class_pattern.findall(rule_key)
            for cls in referenced_classes:
                if cls not in all_classes:
                    raise ValidationError(
                        f"Rule pattern '{rule_key}' contains undefined token class '<{cls}>'.",
                        field_name="rules",
                    )

            # 2. Extract and validate Tokens referenced in rule_key
            # Remove class brackets <...> first so class names aren't confused with tokens
            key_without_classes = class_pattern.sub(" ", rule_key)
            # Remove rule structure brackets ( )
            cleaned_key = token_clean_pattern.sub(" ", key_without_classes)

            # Split tokens by whitespace
            rule_tokens = [t for t in cleaned_key.split() if t]

            for tok in rule_tokens:
                if tok not in all_tokens:
                    raise ValidationError(
                        f"Rule pattern '{rule_key}' contains undefined token '{tok}'.",
                        field_name="rules",
                    )


class TransliterationRuleSchema(Schema):
    production = fields.Str(required=True)
    tokens = fields.List(fields.Str(), required=True)
    prev_classes = fields.List(fields.Str(), allow_none=True)
    next_classes = fields.List(fields.Str(), allow_none=True)
    prev_tokens = fields.List(fields.Str(), allow_none=True)
    next_tokens = fields.List(fields.Str(), allow_none=True)
    cost = fields.Float(required=False, allow_none=True)


class OnMatchRuleSchema(Schema):
    """Schema for OnMatchRule."""

    prev_classes = fields.List(fields.Str())
    next_classes = fields.List(fields.Str())
    production = fields.Str()

    @post_load
    def make_onmatch_rule(self, data: RawOnMatchDict, **kwargs: Any) -> OnMatchRule:
        return _onmatch_rule_of(data)


class SettingsSchema(Schema):
    """Schema for full transliterator settings."""

    tokens = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)
    rules = fields.Nested(TransliterationRuleSchema, many=True, required=True)
    whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
    metadata = fields.Dict(keys=fields.Str(), required=False)
    onmatch_rules = fields.Nested(OnMatchRuleSchema, many=True, required=False)

    @post_load
    def sort_rules_by_cost(self, data: LoadedSettingsDict, **kwargs: Any) -> LoadedSettingsDict:
        """Sort rules by cost."""
        data["rules"] = sorted(data["rules"], key=lambda rule: rule.get("cost", 1.0))
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
                    values = rule.get(property_name)  # Dict access
                    if not values:
                        continue
                    for val in cast(Iterable[Any], values):
                        if val not in token_classes:
                            class_errors[rule_type].append(f'Invalid token class "{val}" in {property_name} of {rule}')

        whitespace = data["whitespace"]
        whitespace_token_class = whitespace["token_class"] if isinstance(whitespace, dict) else whitespace.token_class
        if whitespace_token_class not in token_classes:
            class_errors["whitespace"].append(
                f'Invalid token class "{whitespace_token_class}" in whitespace "{whitespace}".'
            )
        if class_errors:
            raise ValidationError(dict(class_errors))

    # @validates_schema
    # def validate_tokens(self, data: LoadedSettingsDict, **kwargs: Any) -> None:
    #     token_errors: dict[str, list[str]] = defaultdict(list)
    #     token_types = data["tokens"].keys()

    #     whitespace = data["whitespace"]
    #     default_whitespace = whitespace["default"] if isinstance(whitespace, dict) else whitespace.default
    #     if default_whitespace not in token_types:
    #         token_errors["whitespace"].append(f'Invalid default token "{default_whitespace}" in whitespace.')

    #     rules = cast(list[TransliterationRule], data.get("rules"))
    #     if rules:
    #         for rule in rules:
    #             for property_name in ("tokens", "prev_tokens", "next_tokens"):
    #                 values = rule.get(property_name)  # Dict access
    #                 if not values:
    #                     continue
    #                 for val in cast(Iterable[Any], values):
    #                     if val not in token_types:
    #                         token_errors["rules"].append(f'Invalid token "{val}" in {property_name} of rule {rule}')
    #     if token_errors:
    #         raise ValidationError(dict(token_errors))
    @validates_schema
    def validate_tokens(self, data: LoadedSettingsDict, **kwargs: Any) -> None:
        token_errors: dict[str, list[str]] = defaultdict(list)
        token_types = set(data["tokens"].keys())

        whitespace = data["whitespace"]
        default_whitespace = whitespace["default"] if isinstance(whitespace, dict) else whitespace.default
        if default_whitespace not in token_types:
            token_errors["whitespace"].append(f'Invalid default token "{default_whitespace}" in whitespace.')

        rules = data.get("rules")
        if rules:
            for rule in rules:
                for property_name in ("tokens", "prev_tokens", "next_tokens"):
                    # Safely support both dict and object instances
                    if isinstance(rule, dict):
                        values = rule.get(property_name)
                    else:
                        values = getattr(rule, property_name, None)

                    if not values:
                        continue

                    for val in values:
                        if val not in token_types:
                            token_errors["rules"].append(f'Invalid token "{val}" in {property_name} of rule {rule}')

        if token_errors:
            raise ValidationError(dict(token_errors))


# =============================================================================
# HARMONIZED GRAPH SERIALIZATION SCHEMAS
# =============================================================================


class EdgeSchema(Schema):
    source = fields.Int(required=True)
    target = fields.Int(required=True)
    data = fields.Dict(required=True)


class NodeSchema(Schema):
    id = fields.Int(required=True)
    token = fields.Str(required=False)
    type = fields.Str(required=True)
    label = fields.Str(required=False)
    data = fields.Dict(required=True)


class DirectedGraphSchema(Schema):
    """Canonical schema for DirectedGraph matching TypeScript LoadedGraphDict."""

    nodes = fields.Nested(NodeSchema, many=True, required=True)
    edges = fields.Nested(EdgeSchema, many=True, required=True)

    @post_load
    def make_graph(self, data: LoadedGraphDict, **kwargs: Any) -> DirectedGraph:
        _data = copy.deepcopy(data)
        return DirectedGraph(
            nodes=_data.get("nodes", []),
            edges=_data.get("edges", []),
        )


class GraphTransliteratorSchema(Schema):
    """Schema for GraphTransliterator engine dump/load."""

    settings = fields.Nested(SettingsSchema, required=True)
    graph = fields.Nested(DirectedGraphSchema, required=True)
