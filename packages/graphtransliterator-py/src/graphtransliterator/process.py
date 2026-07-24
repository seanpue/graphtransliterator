# -*- coding: utf-8 -*-
"""Functions to process "easy reading" settings of GraphTransliterator."""

import re
from typing import TypeAlias, TypedDict, Union

from .initialize import RawOnMatchDict, RawRuleDict, RawWhitespaceDict

# ==============================================================================
# Descriptive Type Aliases & TypedDicts for Structural Processing Outputs
# ==============================================================================


class ProcessedSettingsDict(TypedDict, total=False):
    """The fully processed and structural shape generated from easy reading."""

    tokens: dict[str, list[str]]
    rules: list[RawRuleDict]
    onmatch_rules: list[RawOnMatchDict]
    whitespace: RawWhitespaceDict
    metadata: dict[str, Union[str, int, float, bool]]


# Helper definition for the dynamic input config blocks
EasyReadingInput: TypeAlias = dict[
    str,
    Union[
        dict[str, str],
        list[dict[str, str]],
        RawWhitespaceDict,
        dict[str, list[str]],
        dict[str, Union[str, int, float, bool]],
    ],
]


# ----------- process settings (main method) ----------


def _process_easyreading_settings(settings: EasyReadingInput) -> ProcessedSettingsDict:
    """Extract information from "easy reading" settings."""

    rules_input = settings.get("rules") or {}
    onmatch_input = settings.get("onmatch_rules") or []

    # Safe downcasting of nested block types since we know their incoming schema shape
    tokens_block = settings.get("tokens") or {}
    whitespace_block = settings.get("whitespace") or {}
    metadata_block = settings.get("metadata") or {}

    return {
        "tokens": tokens_block,  # type: ignore[typeddict-item]
        "rules": _process_rules(rules_input),  # type: ignore[arg-type]
        "onmatch_rules": _process_onmatch_rules(onmatch_input),  # type: ignore[arg-type]
        "whitespace": whitespace_block,  # type: ignore[typeddict-item]
        "metadata": metadata_block,  # type: ignore[typeddict-item]
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


def _process_rule(key: str, value: str) -> RawRuleDict:
    """Convert key and value of a "easy reading" rule into a dict."""

    rule: RawRuleDict = {"production": value}

    match = RULE_RE.match(key)
    if not match:
        raise ValueError(f"Rule pattern is not valid: {key}")

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


def _process_rules(easyreading_rules: dict[str, str]) -> list[RawRuleDict]:
    """Processes "easy reading" rules dict into a list of dict."""

    return [_process_rule(key, value) for key, value in easyreading_rules.items()]


# ----------- process onmatch_rules -----------


ONMATCH_RE = re.compile(r"^(" r"(?:<[^+< \s]+>\s*)+" r")" r"\+" r"(" r"(?:\s*<[^+<]+>)+)\s*$")

ONMATCH_CLASS_RE = re.compile(r"(?<=<)[^+< \s]+(?=>)")


def _process_onmatch_rules(easyreading_onmatch_rules: list[dict[str, str]] | None) -> list[RawOnMatchDict]:
    """Process "easyreading" onmatch_rules (list of dict) into list of dict."""

    if not easyreading_onmatch_rules:
        return []

    processed_onmatch_rules: list[RawOnMatchDict] = []

    for item in easyreading_onmatch_rules:
        if len(item) != 1:
            raise ValueError(f"onmatch_rule has too many values: {item}")

        (rule_easyreading, _production) = list(item.items())[0]

        match = ONMATCH_RE.match(rule_easyreading)
        if not match:
            raise ValueError(f"Onmatch pattern is not valid: {rule_easyreading}")

        prev_str = match.group(1)
        next_str = match.group(2)

        _prev_classes = ONMATCH_CLASS_RE.findall(prev_str)
        _next_classes = ONMATCH_CLASS_RE.findall(next_str)

        onmatch_rule_processed: RawOnMatchDict = {
            "prev_classes": _prev_classes,
            "next_classes": _next_classes,
            "production": _production,
        }

        processed_onmatch_rules.append(onmatch_rule_processed)

    return processed_onmatch_rules
