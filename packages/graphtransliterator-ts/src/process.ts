// src/process.ts

import {
    RawRuleDict,
    RawOnMatchDict,
    RawWhitespaceDict,
    EasyReadingInput,
    ProcessedSettingsDict,
} from "./types.js";

// ----------- Regex Patterns ----------

// Regex matching rule syntax key string
const RULE_RE =
    /^(?:\(((?:\s?<.+?>\s+)+)?(.+?)\s?\)\s|((?:\s?<.+?>\s+)+)?)?((?:\n|\r|.)+?)(?:\s+\((.+?)((?:\s+<.+?>?)?)\)$|((?:\s+<.+?>)+)|$)/;

// Regex matching onmatch rule syntax key string
const ONMATCH_RE = /^((?:<[^+< \s]+>\s*)+)\+((?:\s*<[^+<]+>)+)\s*$/;
const ONMATCH_CLASS_RE = /<([^+< \s]+)>/g;

// ----------- Helper Regex Extractors ----------

function matchAllAngleBrackets(str: string): string[] {
    const matches: string[] = [];
    const regex = /<(.+?)>/g;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(str)) !== null) {
        matches.push(match[1]);
    }
    return matches;
}

// ----------- process rules ----------

/** Convert key and value of an "easy reading" rule into a dict. */
export function processRule(key: string, value: string): RawRuleDict {
    const rule: RawRuleDict = { production: value, tokens: [] };

    const match = RULE_RE.exec(key);
    if (!match) {
        throw new Error(`Rule pattern is not valid: ${key}`);
    }

    // Groups:
    // 1: prev_classes inside parentheses
    // 2: prev_tokens inside parentheses
    // 3: prev_classes outside parentheses
    // 4: tokens
    // 5: next_tokens inside parentheses
    // 6: next_classes inside parentheses
    // 7: next_classes outside parentheses

    if (match[1]) {
        rule.prev_classes = matchAllAngleBrackets(match[1]);
    }
    if (match[2]) {
        rule.prev_tokens = match[2].split(" ");
    }
    if (match[3]) {
        rule.prev_classes = matchAllAngleBrackets(match[3]);
    }

    if (match[4] === " ") {
        rule.tokens = [" "];
    } else {
        rule.tokens = match[4].split(" ").filter((x) => x !== "");
    }

    if (match[5]) {
        rule.next_tokens = match[5].split(" ");
    }
    if (match[6]) {
        rule.next_classes = matchAllAngleBrackets(match[6]);
    }
    if (match[7]) {
        rule.next_classes = matchAllAngleBrackets(match[7]);
    }

    return rule;
}

/** Processes "easy reading" rules dict into a list of rule objects. */
export function processRules(
    easyreadingRules: Record<string, string>,
): RawRuleDict[] {
    return Object.entries(easyreadingRules).map(([key, value]) =>
        processRule(key, value),
    );
}

// ----------- process onmatch_rules -----------

/** Process "easyreading" onmatch_rules into list of dict. */
export function processOnMatchRules(
    easyreadingOnmatchRules?: Record<string, string>[] | null,
): RawOnMatchDict[] {
    if (!easyreadingOnmatchRules || easyreadingOnmatchRules.length === 0) {
        return [];
    }

    const processedOnmatchRules: RawOnMatchDict[] = [];

    for (const item of easyreadingOnmatchRules) {
        const entries = Object.entries(item);
        if (entries.length !== 1) {
            throw new Error(
                `onmatch_rule has too many values: ${JSON.stringify(item)}`,
            );
        }

        const [ruleEasyreading, production] = entries[0];
        const match = ONMATCH_RE.exec(ruleEasyreading);
        if (!match) {
            throw new Error(`Onmatch pattern is not valid: ${ruleEasyreading}`);
        }

        const prevStr = match[1];
        const nextStr = match[2];

        const prevClasses: string[] = [];
        let prevMatch: RegExpExecArray | null;
        ONMATCH_CLASS_RE.lastIndex = 0;
        while ((prevMatch = ONMATCH_CLASS_RE.exec(prevStr)) !== null) {
            prevClasses.push(prevMatch[1]);
        }

        const nextClasses: string[] = [];
        let nextMatch: RegExpExecArray | null;
        ONMATCH_CLASS_RE.lastIndex = 0;
        while ((nextMatch = ONMATCH_CLASS_RE.exec(nextStr)) !== null) {
            nextClasses.push(nextMatch[1]);
        }

        processedOnmatchRules.push({
            prev_classes: prevClasses,
            next_classes: nextClasses,
            production,
        });
    }

    return processedOnmatchRules;
}

// ----------- process settings (main method) ----------

/** Extract information from "easy reading" settings. */
export function processEasyReadingSettings(
    settings: EasyReadingInput,
): ProcessedSettingsDict {
    const rulesInput = (settings.rules as Record<string, string>) || {};
    const onmatchInput =
        (settings.onmatch_rules as Record<string, string>[]) || [];

    const tokensBlock = (settings.tokens as Record<string, string[]>) || {};
    const whitespaceBlock = (settings.whitespace as RawWhitespaceDict) || {};
    const metadataBlock = (settings.metadata as Record<string, any>) || {};

    return {
        tokens: tokensBlock,
        rules: processRules(rulesInput),
        onmatch_rules: processOnMatchRules(onmatchInput),
        whitespace: whitespaceBlock,
        metadata: metadataBlock,
    };
}
