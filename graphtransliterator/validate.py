# -*- coding: utf-8 -*-
"""Methods and schemas to validate GraphTransliterator parameters."""

import yaml
from cerberus import Validator
from .process import RULE_RE, ONMATCH_RE

# ---------- validate easy reading settings ----------

EASYREADING_SETTINGS_SCHEMA = yaml.safe_load(
    '''
    rules:
        type: dict
        required: True
        keysrules:
            type: string
            regex: {rule_regex}
        valuesrules:
            type: string
    onmatch_rules:
        type: list
        required: False
        schema:
            type: dict
            minlength: 1
            maxlength: 1
            keysrules:
                type: string
                regex: {onmatch_regex}
            valuesrules:
                type: string
    tokens:
        type: dict
        required: True
        keysrules:
            type: string
        valuesrules:
            type: list
            schema:
                type: string
    whitespace:
        type: dict
        required: True
        schema:
            default:
                required: True
                type: string
            token_class:
                required: True
                type: string
            consolidate:
                required: True
                type: boolean
    metadata:
        type: dict
        required: False
    '''.format(rule_regex=RULE_RE.pattern,
               onmatch_regex=ONMATCH_RE.pattern)
)


def validate_easyreading_settings(settings):
    """
    Validate general structure of "easy reading" settings, e.g.
    structure of YAML

    Parameters
    ----------
    settings : dict
        Easy reading settings to validate
    Raises
    ------
    ValueError
        If the easy reading settings do not validate.
    """
    validator = Validator()
    validator.validate(settings, EASYREADING_SETTINGS_SCHEMA, normalize=False)
    if validator.errors:
        raise ValueError("Errors in GraphTransliterator settings: \n %s" %
                         validator.errors)

# ---------- validate settings ----------


def validate_settings(tokens, rules, onmatch_rules, whitespace, metadata):
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
    validator = Validator()

    tokens_schema = yaml.safe_load("""
        tokens:
            type: dict
            keysrules:
                type: string
            valuesrules:
                type: list
                schema:
                    type: string
    """)

    validator.validate({'tokens': tokens}, tokens_schema)

    if validator.errors:
        raise ValueError(
            "GraphTransliterator `tokens` contains invalid entries:\n %s" %
            validator.errors)

    token_keys = list(tokens.keys())
    token_classes = list(set().union(*tokens.values()))

    rules_schema = {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'tokens': {
                    'required': True,
                    'type': 'list',
                    'allowed': token_keys,
                },
                'prev_classes': {
                    'required': False,
                    'type': 'list',
                    'allowed': token_classes,
                },
                'prev_tokens': {
                    'required': False,
                    'type': 'list',
                    'allowed': token_keys,
                },
                'next_tokens': {
                    'required': False,
                    'type': 'list',
                    'allowed': token_keys,
                },
                'next_classes': {
                    'required': False,
                    'type': 'list',
                    'allowed': token_classes,
                },
                'production': {
                    'required': True,
                    'type': 'string',
                },
            }
        }
    }

    onmatch_rules_schema = {
        'type': 'list',
        'required': False,
        'schema': {
            'type': 'dict',
            'schema': {
                'prev_classes':  {
                    'type': 'list',
                    'schema': {
                        'allowed': token_classes
                    }
                },
                'production': {
                    'type': 'string',
                },
                'next_classes': {
                    'type': 'list',
                    'schema': {
                        'allowed': token_classes
                    }
                }
            }
        }
    }

    whitespace_schema = {
        'type': 'dict',
        'required': True,
        'schema': {
            'default': {
                'type': 'string',
                'allowed': token_keys
            },
            'token_class': {
                'type': 'string',
                'allowed': token_classes
            },
            'consolidate': {
                'type': 'boolean'
            }
        }
    }

    metadata_schema = {
        'type': 'dict',
        'required': False
    }

    schemas = {'whitespace': whitespace_schema,
               'onmatch_rules': onmatch_rules_schema,
               'rules': rules_schema,
               'metadata': metadata_schema}

    document = {'whitespace': whitespace,
                'rules': rules,
                'onmatch_rules': onmatch_rules,
                'metadata': metadata}  # Cerberus needs a dict

    validator.validate(document, schemas)

    if validator.errors:
        raise ValueError(
            "GraphTransliterator settings contain invalid entries:\n%s" %
            validator.errors
        )
