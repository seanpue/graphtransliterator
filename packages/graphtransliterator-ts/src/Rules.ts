// src/Rules.ts
/**
 * This module defines GraphTransliterator rules.
 */

// ---------- Tokens ----------

/** Individual token for a `GraphTransliterator`, e.g. "aa" */
export type Token = string;

/** Array of `Token` */
export type Tokens = Token[];

/** Class of a token, e.g. 'consonant'. */
export type TokenClass = string;

/** Array of `TokenClass` */
export type TokenClasses = TokenClass[];

/** String output produced by a particular `TransliterationRule` or `OnMatchRule` */
export type Production = string;

export type Cost = number;

// ---------- Rules ----------

/**
 * A transliteration rule containing the specific match conditions and
 * string output to be produced, as well as the rule's cost.
 */
export interface TransliterationRule {
	production: Production;
	prevClasses?: TokenClasses | null;
	prevTokens?: Tokens | null;
	tokens: Tokens;
	nextTokens?: Tokens | null;
	nextClasses?: TokenClasses | null;
	cost: Cost;
}

/** Array of `TransliterationRule` */
export type TransliterationRules = TransliterationRule[];

// ---------- Whitespace ----------

/**
 * Whitespace rules of a GraphTransliterator
 */
export interface WhitespaceRule {
	consolidate: boolean;
	/** Standard token substitution for consolidated whitespace chunks. */
	default: Token;
	tokenClass: TokenClass;
}

// ---------- On Match ----------

/**
 * Rules about adding text between certain combinations of matched rules.
 */
export interface OnMatchRule {
	prevClasses: TokenClasses;
	nextClasses: TokenClasses;
	production: Production;
}

/** Array of `OnMatchRule` */
export type OnMatchRules = OnMatchRule[];

/** Identifier for an `OnMatchRule` by its index in `OnMatchRules` */
export type OnMatchRuleId = number;

/** Array of `OnMatchRuleId` */
export type OnMatchRuleIds = OnMatchRuleId[];

// ---------- Helper Methods ----------

/** Calculate number of tokens in a rule. */
function numTokensOf(
	prevClasses: TokenClasses | null | undefined,
	prevTokens: Tokens | null | undefined,
	tokens: Tokens,
	nextTokens: Tokens | null | undefined,
	nextClasses: TokenClasses | null | undefined,
): number {
	const maybeLen = <T>(arr: T[] | null | undefined): number => arr?.length ?? 0;

	return (
		maybeLen(prevClasses) +
		maybeLen(prevTokens) +
		tokens.length +
		maybeLen(nextTokens) +
		maybeLen(nextClasses)
	);
}

/**
 * Calculate cost of a rule.
 *
 * Rules with more total constraints (prev/next classes/tokens + matched tokens)
 * have lower cost and should be tried first (i.e. sort ascending by cost).
 */
export function costOf(
	prevClasses: TokenClasses | null | undefined,
	prevTokens: Tokens | null | undefined,
	tokens: Tokens,
	nextTokens: Tokens | null | undefined,
	nextClasses: TokenClasses | null | undefined,
): Cost {
	const n: number = numTokensOf(
		prevClasses,
		prevTokens,
		tokens,
		nextTokens,
		nextClasses,
	);
	return 1 / (1 + n);
}
