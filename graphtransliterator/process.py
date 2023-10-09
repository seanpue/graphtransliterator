# -*- coding: utf-8 -*-
"""
Functions to process "easy reading" settings of GraphTransliterator.
"""

import re


# ----------- process settings (main method) ----------


def _process_easyreading_settings(settings):
    """
    Extract information from "easy reading" settings.

    Returns
    -------
    `dict` keyed by:
      `tokens`: dict of {str: list of str}
      `rules`:  list of dict {'prev_classes', 'prev_tokens', 'tokens',
                'next_tokens', 'next_classes'}
      `whitespace': dict {'default', 'token_class', 'consolidate'}
      `onmatch_rules`: list of dict {
                       'prev_classes', 'next_classes', 'production'}
    """

    return {
        "tokens": settings.get("tokens"),
        "rules": _process_rules(settings.get("rules")),
        "onmatch_rules": _process_onmatch_rules(settings.get("onmatch_rules")),
        "whitespace": settings.get("whitespace"),
        "metadata": settings.get("metadata", {}),
    }


# ----------- process rules ----------

# added \n and \r explicitly as validator does not accept re.DOTALL

RULE_RE = re.compile(
    r"(?:\(((?:\s?<.+?>\s+)+)?(.+?)\s?\) |((?:\s?<.+?>\s+)+)?)?"
    r"((?:\n|\r|.)+?)"
    r"(?:"
    r"\s+(?:\((.+?)((?:\s+<.+?>?)?)\)$)"
    r"|"
    r"((?:\s+<.+?>)+)"
    r"|"
    r"$)"
)


def _process_rule(key, value):
    """Convert key and value of a "easy reading" rule into a dict."""

    rule = {"production": value}  # needs to be dict for Cerberus

    match = RULE_RE.match(key)
    assert match, "Rule pattern is not valid: %s" % key

    if match.group(1):
        rule["prev_classes"] = re.findall("<(.+?)>", match.group(1))
    if match.group(2):
        rule["prev_tokens"] = match.group(2).split(" ")
    if match.group(3):
        rule["prev_classes"] = re.findall("<(.+?)>", match.group(3))
    if match.group(4) == " ":
        rule["tokens"] = [" "]
    else:
        rule["tokens"] = [x for x in match.group(4).split(" ") if x != ""]
    if match.group(5):
        rule["next_tokens"] = match.group(5).split(" ")
    if match.group(6):
        rule["next_classes"] = re.findall("<(.+?)>", match.group(6))
    if match.group(7):
        rule["next_classes"] = re.findall("<(.+?)>", match.group(7))

    return rule


def _process_rules(easyreading_rules):
    """Processes "easy reading" rules dict into a list of dict."""

    return [_process_rule(key, value) for key, value in easyreading_rules.items()]


# ----------- process onmatch_rules -----------


ONMATCH_RE = re.compile(
    r"^(" r"(?:<[^+< \s]+>\s*)+" r")" r"\+" r"(" r"(?:\s*<[^+<]+>)+)\s*$"
)

ONMATCH_CLASS_RE = re.compile(r"(?<=<)[^+< \s]+(?=>)")


def _process_onmatch_rules(easyreading_onmatch_rules):
    """Process "easyreading" onmatch_rules (list of dict) into list of dict."""

    if not easyreading_onmatch_rules:
        return []

    processed_onmatch_rules = []

    for item in easyreading_onmatch_rules:
        assert len(item) == 1, "onmatch_rule has too many values: %s" % item

        (rule_easyreading, _production) = list(item.items())[0]

        match = ONMATCH_RE.match(rule_easyreading)

        prev_str = match.group(1)
        next_str = match.group(2)

        _prev_classes = ONMATCH_CLASS_RE.findall(prev_str)
        _next_classes = ONMATCH_CLASS_RE.findall(next_str)

        onmatch_rule_processed = {
            "prev_classes": _prev_classes,
            "next_classes": _next_classes,
            "production": _production,
        }

        processed_onmatch_rules.append(onmatch_rule_processed)

    return processed_onmatch_rules
