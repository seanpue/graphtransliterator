# -*- coding: utf-8 -*-
"""Methods to process easy-reading raw strings of GraphTransliterator input."""

import re


# ----------- process settings (main method) ----------


def _process_settings(settings):
    """Convert easy-reading into raw settings."""

    processed_settings = {
        'tokens': settings.get('tokens'),
        'rules': _process_rules(settings.get('rules')),
        'onmatch_rules': _process_onmatch_rules(settings.get('onmatch_rules')),
        'whitespace': settings.get('whitespace'),
        'metadata': settings.get('metatdata', {})
    }
    return processed_settings


# ----------- process rules ----------

# added \n and \r explicitly as validator does not accept re.DOTALL

RULE_RE = re.compile(
    r'(?:\(((?:\s?<.+?>\s+)+)?(.+?)\s?\) |((?:\s?<.+?>\s+)+)?)?'
    r'((?:\n|\r|.)+?)'
    r'(?:'
    r'\s+(?:\((.+?)((?:\s+<.+?>?)?)\)$)'
    r'|'
    r'((?:\s+<.+?>)+)'
    r'|'
    r'$)'
)


def _process_rule(key, value):
    """Convert key and value of a raw rule into a dict."""

    rule = {'production': value}               # needs to be dict for Cerberus

    match = RULE_RE.match(key)
    assert match, 'Rule pattern is not valid: %s' % key

    if match.group(1):
        rule['prev_classes'] = re.findall('<(.+?)>', match.group(1))
    if match.group(2):
        rule['prev_tokens'] = match.group(2).split(' ')
    if match.group(3):
        rule['prev_classes'] = re.findall('<(.+?)>', match.group(3))
    if match.group(4) == ' ':
        rule['tokens'] = [' ']
    else:
        rule['tokens'] = [x for x in match.group(4).split(' ') if x != '']
    if match.group(5):
        rule['next_tokens'] = match.group(5).split(' ')
    if match.group(6):
        rule['next_classes'] = re.findall('<(.+?)>', match.group(6))
    if match.group(7):
        rule['next_classes'] = re.findall('<(.+?)>', match.group(7))

    return rule


def _process_rules(raw_rules):
    """Processes raw rules dict into a list of dict of processed rules."""

    return [_process_rule(key, value) for key, value in raw_rules.items()]


# ----------- process onmatch_rules -----------


ONMATCH_RE = re.compile(
    r'^('
    r'(?:<[^+< \s]+>\s*)+'
    r')'
    r'\+'
    r'('
    r'(?:\s*<[^+<]+>)+)\s*$'
)

ONMATCH_CLASS_RE = re.compile(
    r'(?<=<)[^+< \s]+(?=>)'
)


def _process_onmatch_rules(raw_onmatch_rules):
    """Process onmatch_rules (list of dict) into list of OnMatchRules."""

    if not raw_onmatch_rules:
        return []

    processed_onmatch_rules = []

    for item in raw_onmatch_rules:

        assert len(item) == 1, "onmatch_rule has too many values: %s" % item

        (rule_raw, _production) = list(item.items())[0]

        match = ONMATCH_RE.match(rule_raw)

        prev_str = match.group(1)
        next_str = match.group(2)

        _prev_classes = ONMATCH_CLASS_RE.findall(prev_str)
        _next_classes = ONMATCH_CLASS_RE.findall(next_str)

        onmatch_rule_processed = {
            'prev_classes': _prev_classes,
            'next_classes': _next_classes,
            'production': _production
        }

        processed_onmatch_rules.append(onmatch_rule_processed)

    return processed_onmatch_rules
