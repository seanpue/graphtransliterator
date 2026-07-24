// src/initialize.ts

import type { Token, TransliterationRule } from "./types.js";

export function numTokensOf(rule: TransliterationRule): number {
	const mainTokens = rule.tokens.length;
	const prevClasses = rule.prev_classes?.length ?? 0;
	const prevTokens = rule.prev_tokens?.length ?? 0;
	const nextTokens = rule.next_tokens?.length ?? 0;
	const nextClasses = rule.next_classes?.length ?? 0;

	return mainTokens + prevClasses + prevTokens + nextTokens + nextClasses;
}

export function costOf(rule: TransliterationRule): number {
	const numTokens = numTokensOf(rule);
	return Math.log2(1 + 1 / (1 + numTokens));
}

export function transliterationRuleOf(
	rawRule: Partial<TransliterationRule> & {
		tokens: string[];
		production: string;
	},
): TransliterationRule {
	const rule: TransliterationRule = {
		tokens: rawRule.tokens,
		production: rawRule.production,
		cost: rawRule.cost ?? 0,
		...(rawRule.prev_classes && { prev_classes: rawRule.prev_classes }),
		...(rawRule.prev_tokens && { prev_tokens: rawRule.prev_tokens }),
		...(rawRule.next_tokens && { next_tokens: rawRule.next_tokens }),
		...(rawRule.next_classes && { next_classes: rawRule.next_classes }),
	};

	if (rawRule.cost === undefined) {
		rule.cost = costOf(rule);
	}

	return rule;
}

export function tokensByClassOf(
	tokenDict: Record<string, string[]>,
): Map<string, Set<string>> {
	const tbc = new Map<string, Set<string>>();
	for (const [token, classes] of Object.entries(tokenDict)) {
		for (const cls of classes) {
			if (!tbc.has(cls)) tbc.set(cls, new Set());
			tbc.get(cls)!.add(token);
		}
	}
	return tbc;
}

function escapeRegex(str: string): string {
	return str.replace(/[.*+?^${}()|[\]/\\]/g, "\\$&");
}

export function tokenizerPatternStrFrom(tkns: Token[]): string {
	const sorted = [...tkns].sort((a, b) => {
		if (b.length !== a.length) {
			return b.length - a.length;
		}
		return a < b ? -1 : a > b ? 1 : 0;
	});
	return `(${sorted.map(escapeRegex).join("|")})`;
}

export function tokenizerPatternFrom(tkns: Token[]): RegExp | string {
	return tokenizerPatternStrFrom(tkns);
}
