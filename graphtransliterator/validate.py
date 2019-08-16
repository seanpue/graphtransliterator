# -*- coding: utf-8 -*-
"""Methods and schemas to validate GraphTransliterator parameters."""

# from cerberus import Validator
from collections import defaultdict
from .process import RULE_RE, ONMATCH_RE

from marshmallow import fields, Schema, validate, ValidationError, validates_schema

# ----- Marshmallow schemas


class WhitespaceSettingsSchema(Schema):
    default = fields.Str(required=True)
    token_class = fields.Str(required=True)
    consolidate = fields.Boolean(required=True)


class EasyReadingSettingsSchema(Schema):
    tokens = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.Str()), required=True
    )
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
    whitespace = fields.Nested(WhitespaceSettingsSchema)


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()


class RuleSchema(Schema):
    production = fields.Str()
    tokens = fields.List(fields.Str())
    prev_classes = fields.List(fields.Str())
    next_classes = fields.List(fields.Str())
    prev_tokens = fields.List(fields.Str())
    next_tokens = fields.List(fields.Str())


class OnMatchRuleSchema(Schema):
    prev_classes = fields.List(fields.Str())
    next_classes = fields.List(fields.Str())
    production = fields.Str()


class SettingsSchema(Schema):
    tokens = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.Str()), required=True
    )
    rules = fields.Nested(RuleSchema, many=True, required=True)
    whitespace = fields.Nested(WhitespaceSettingsSchema, many=False, required=True)
    metadata = fields.Dict(
        keys=fields.Str(), required=False  # no restriction on values
    )
    onmatch_rules = fields.Nested(OnMatchRuleSchema, many=True, required=False)
    whitespace = fields.Nested(WhitespaceSettingsSchema, required=True)

    from collections import defaultdict

    @validates_schema
    def validate_token_classes(self, data, **kwargs):
        errors = defaultdict(list)
        token_classes = list(set().union(*data["tokens"].values()))

        # validate onmatch_rules and rules
        for rule_type in ("onmatch_rules", "rules"):
            for rule in data[rule_type]:
                for component in ("prev_classes", "next_classes"):
                    for _ in rule.get(component, []):
                        if _ not in token_classes:
                            errors[rule_type].append(
                                'Invalid token class "{}" in {} of {}'.format(
                                    _, component, rule
                                )
                            )

        # validate whitespace token_class
        whitespace = data["whitespace"]
        whitespace_token_class = whitespace["token_class"]
        if whitespace_token_class not in token_classes:
            errors["whitespace"].append(
                'Invalid token class "{}" in whitespace.'.format(
                    whitespace_token_class, whitespace
                )
            )
        if errors:
            raise ValidationError(dict(errors))

    @validates_schema
    def validate_tokens(self, data, **kwargs):
        errors = defaultdict(list)
        token_types = data["tokens"].keys()

        # validate whitespace
        whitespace = data["whitespace"]
        default_whitespace = whitespace["default"]
        if default_whitespace not in token_types:
            errors["whitespace"].append(
                'Invalid default token "{}" in whitespace.'.format(default_whitespace)
            )

        # validate rules
        rules = data["rules"]
        for rule in rules:
            for component in ("tokens", "prev_tokens", "next_tokens"):
                for _ in rule.get(component, []):
                    if _ not in token_types:
                        errors["rules"].append(
                            'Invalid token "{}" in {} of rule {}'.format(
                                _, component, rule
                            )
                        )
        if errors:
            raise ValidationError(dict(errors))


# ---------- validate easy reading settings ----------


# EASYREADING_SETTINGS_SCHEMA = {
#     "rules": {
#         "type": "dict",
#         "required": True,
#         "keysrules": {"type": "string", "regex": RULE_RE.pattern},
#         "valuesrules": {"type": "string"},
#     },
#     "onmatch_rules": {
#         "type": "list",
#         "required": False,
#         "schema": {
#             "type": "dict",
#             "minlength": 1,
#             "maxlength": 1,
#             "keysrules": {"type": "string", "regex": ONMATCH_RE.pattern},
#             "valuesrules": {"type": "string"},
#         },
#     },
#     "tokens": {
#         "type": "dict",
#         "required": True,
#         "keysrules": {"type": "string"},
#         "valuesrules": {"type": "list", "schema": {"type": "string"}},
#     },
#     "whitespace": {
#         "type": "dict",
#         "required": True,
#         "schema": {
#             "default": {"required": True, "type": "string"},
#             "token_class": {"required": True, "type": "string"},
#             "consolidate": {"required": True, "type": "boolean"},
#         },
#     },
#     "metadata": {"type": "dict", "required": False},
# }
#
#
# def validate_easyreading_settings_cerberus(settings):
#     """
#     Validate general structure of "easy reading" settings, e.g.
#     structure of YAML
#
#     Parameters
#     ----------
#     settings : dict
#         Easy reading settings to validate
#     Raises
#     ------
#     ValueError
#         If the easy reading settings do not validate.
#     """
#     validator = Validator()
#     validator.validate(settings, EASYREADING_SETTINGS_SCHEMA, normalize=False)
#     if validator.errors:
#         raise ValueError(
#             "Errors in GraphTransliterator settings: \n %s" % validator.errors
#         )


def validate_easyreading_settings_marshmallow(settings):
    """
    Validate general structure of "easy reading" settings, e.g.
    structure of YAML

    Parameters
    ----------
    settings : dict
        Easy reading settings to validate
    Raises
    ------
    marshmallow.ValidationError
        If the easy reading settings do not validate.
    """
    EasyReadingSettingsSchema().load(settings)


def validate_easyreading_settings(settings, use_marshmallow=True):
    # if use_marshmallow:
    validate_easyreading_settings_marshmallow(settings)
    # else:
    #    validate_easyreading_settings_cerberus(settings)


# ---------- validate settings ----------


# def validate_settings_cerberus(tokens, rules, onmatch_rules, whitespace, metadata):
#     """
#     Validate processed settings for GraphTransliterator.
#
#     This method first checks the tokens, then uses the tokens and token
#     classes to validate the rules, onmatch rules, whitespace settings,
#     all of which need the information from the tokens. Then it checks the
#     metadata settings are a dictionary.
#
#     Parameters
#     ----------
#     tokens: dict of {str : list of str}
#         Tokens and their classes
#     rules: list of dict {str: str}
#         Transliteration rules in easy reading format
#     onmatch_rules: list of dict {str: str}
#         Rules for productions between matches of token classes
#     whitespace: {'default':str, 'token_class':str, 'consolidate':bool}
#         Whitespace parameters
#     metadata: dict {str: str}
#         Metadata settings
#     Raises
#     ------
#     ValueError
#         If there are validations errors in the "easy reading" settings
#     """
#     validator = Validator()
#
#     tokens_schema = {
#         "tokens": {
#             "keysrules": {"type": "string"},
#             "type": "dict",
#             "valuesrules": {"schema": {"type": "string"}, "type": "list"},
#         }
#     }
#
#     validator.validate({"tokens": tokens}, tokens_schema)
#
#     if validator.errors:
#         raise ValueError(
#             "GraphTransliterator `tokens` contains invalid entries:\n %s"
#             % validator.errors
#         )
#
#     token_keys = list(tokens.keys())
#     token_classes = list(set().union(*tokens.values()))
#
#     rules_schema = {
#         "type": "list",
#         "schema": {
#             "type": "dict",
#             "schema": {
#                 "tokens": {"required": True, "type": "list", "allowed": token_keys},
#                 "prev_classes": {
#                     "required": False,
#                     "type": "list",
#                     "allowed": token_classes,
#                 },
#                 "prev_tokens": {
#                     "required": False,
#                     "type": "list",
#                     "allowed": token_keys,
#                 },
#                 "next_tokens": {
#                     "required": False,
#                     "type": "list",
#                     "allowed": token_keys,
#                 },
#                 "next_classes": {
#                     "required": False,
#                     "type": "list",
#                     "allowed": token_classes,
#                 },
#                 "production": {"required": True, "type": "string"},
#             },
#         },
#     }
#
#     onmatch_rules_schema = {
#         "type": "list",
#         "required": False,
#         "schema": {
#             "type": "dict",
#             "schema": {
#                 "prev_classes": {"type": "list", "schema": {"allowed": token_classes}},
#                 "production": {"type": "string"},
#                 "next_classes": {"type": "list", "schema": {"allowed": token_classes}},
#             },
#         },
#     }
#
#     whitespace_schema = {
#         "type": "dict",
#         "required": True,
#         "schema": {
#             "default": {"type": "string", "allowed": token_keys},
#             "token_class": {"type": "string", "allowed": token_classes},
#             "consolidate": {"type": "boolean"},
#         },
#     }
#
#     metadata_schema = {"type": "dict", "required": False}
#
#     schemas = {
#         "whitespace": whitespace_schema,
#         "onmatch_rules": onmatch_rules_schema,
#         "rules": rules_schema,
#         "metadata": metadata_schema,
#     }
#
#     document = {
#         "whitespace": whitespace,
#         "rules": rules,
#         "onmatch_rules": onmatch_rules,
#         "metadata": metadata,
#     }  # Cerberus needs a dict
#
#     validator.validate(document, schemas)
#
#     if validator.errors:
#         raise ValueError(
#             "GraphTransliterator settings contain invalid entries:\n%s"
#             % validator.errors
#         )
#
#
def validate_settings_marshmallow(tokens, rules, onmatch_rules, whitespace, metadata):
    SettingsSchema().load(
        {
            "tokens": tokens,
            "rules": rules,
            "onmatch_rules": onmatch_rules,
            "whitespace": whitespace,
            "metadata": metadata,
        }
    )


def validate_settings(
    tokens, rules, onmatch_rules, whitespace, metadata, use_marshmallow=True
):
    """
    Validate processed settings for GraphTransliterator.

    This method first checks the tokens, then uses the tokens and token
    classes to validate the rules, onmatch rules, whitespace settings,
    all of which need the information from the tokens. Then it checks the
    metadata settings are a dictionary.

    Parameters
    ----------
    tokens: dict of {str : list of str}
        Tokens and their classes
    rules: list of dict {str: str}
        Transliteration rules in easy reading format
    onmatch_rules: list of dict {str: str}
        Rules for productions between matches of token classes
    whitespace: {'default':str, 'token_class':str, 'consolidate':bool}
        Whitespace parameters
    metadata: dict {str: str}
        Metadata settings
    Raises
    ------
    ValueError
        If there are validations errors in the "easy reading" settings
    """
    # if use_marshmallow:

    validate_settings_marshmallow(tokens, rules, onmatch_rules, whitespace, metadata)
    # else:
    #    validate_settings_cerberus(tokens, rules, onmatch_rules, whitespace, metadata)
