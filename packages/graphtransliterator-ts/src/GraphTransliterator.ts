// src/GraphTransliterator.ts

/**
 * @module GraphTransliterator
 */

import yaml from "yaml";
import { DirectedGraph } from "./Graphs.js";
import { costOf } from "./initialize.js";
import type {
	EasyReadingSettings,
	GraphTransliteratorConfig,
	GTEdge,
	GTGraph,
	GTNode,
	MatchAtResult,
	MatchesAtResults,
	Metadata,
	NodeId,
	OnMatchRules,
	OnMatchRulesLookup,
	Production,
	RawEasyReadingSettings,
	RuleId,
	Token,
	TokenClass,
	TokenClasses,
	Tokens,
	TokensByClass,
	TransliterationReport,
	TransliterationRule,
	TransliterationRules,
	WhitespaceRule,
} from "./types.js";

export class GraphTransliterator {
	tokens: Record<Token, TokenClasses>;
	rules: TransliterationRules;
	whiteSpace: WhitespaceRule;
	onMatchRules?: OnMatchRules;
	metadata?: Metadata;
	onMatchRulesLookup?: OnMatchRulesLookup;
	tokensByClass: TokensByClass;
	tokenizerPattern: RegExp;
	tokenizerPatternStr: string;
	graph: GTGraph;

	constructor(config: {
		tokens: Record<Token, TokenClasses>;
		rules: TransliterationRules;
		whitespace: WhitespaceRule;
		onMatchRules?: OnMatchRules;
		metadata?: Metadata;
		onMatchRulesLookup?: OnMatchRulesLookup;
		tokensByClass: TokensByClass;
		tokenizerPattern: RegExp;
		tokenizerPatternStr: string;
		graph: GTGraph;
	}) {
		this.tokens = config.tokens;
		this.rules = config.rules;
		this.whiteSpace = config.whitespace;
		this.onMatchRules = config.onMatchRules;
		this.metadata = config.metadata;
		this.onMatchRulesLookup = config.onMatchRulesLookup;
		this.tokensByClass = config.tokensByClass;
		this.tokenizerPattern = config.tokenizerPattern;
		this.tokenizerPatternStr = config.tokenizerPatternStr;
		this.graph = config.graph;
	}

	/**
	 * Transliterates an input string using this instance's rules and configuration.
	 */
	public transliterate(input: string): string {
		return transliterate(input, this);
	}

	/**
	 * Generates a detailed transliteration report for an input string.
	 */
	public transliterateReporting(input: string): TransliterationReport {
		return transliterateReporting(input, this);
	}

	/**
	 * Tokenizes an input string based on this instance's token definitions.
	 */
	public tokenize(input: string): Tokens {
		return tokenize(input, this);
	}

	/**
	 * Finds all rule matches at a given token index.
	 */
	public matchRulesAt(tokenIdx: number, tokens: Tokens): MatchesAtResults {
		return matchRulesAt(tokenIdx, tokens, this);
	}

	/**
	 * Creates a new GraphTransliterator instance pruned of specific productions.
	 */
	public prunedOf(productions: string | string[]): GraphTransliterator {
		const prodSet = new Set(
			typeof productions === "string" ? [productions] : productions,
		);

		const prunedRules = this.rules.filter(
			(rule) => !prodSet.has(rule.production),
		);

		return graphTransliterator({
			tokens: this.tokens,
			rules: prunedRules,
			whitespace: this.whiteSpace,
			onMatchRules: this.onMatchRules,
			metadata: this.metadata,
		});
	}
}

const easyReadingRuleRegex =
	/^(?:\(((?:\s?<.+?>\s+)+)?(.+?)\s?\) |((?:\s?<.+?>\s+)+)?)?((?:\n|\r|.)+?)(?:\s+(?:\((.+?)((?:\s+<.+?>?)?)\)$)|((?:\s+<.+?>)+)|$)/;

const classesRegex = /<(.+?)>/g;
const easyReadingOnMatchRuleRegex =
	/^((?:<[^+<\s]+>\s*)+)\+((?:\s*<[^+<]+>)+)\s*$/;

function getClasses(z: string): string[] {
	const matches: string[] = [];
	const regex = new RegExp(classesRegex, "g");

	for (const match of z.matchAll(regex)) {
		if (match[1]) matches.push(match[1]);
	}
	return matches;
}

function getPrevClasses(m: (string | undefined)[]): TokenClasses | null {
	const validMatch = m[1] || m[3];
	if (!validMatch) return null;
	return getClasses(validMatch);
}

function getPrevTokens(m: (string | undefined)[]): Tokens | null {
	const oneMatch = m[2];
	if (!oneMatch) return null;
	return oneMatch.split(" ").filter(Boolean);
}

function getTokens(m: (string | undefined)[]): Tokens | null {
	const fourMatch = m[4];
	if (fourMatch === " ") return [" "];
	if (!fourMatch) return null;
	return fourMatch.split(" ").filter(Boolean);
}

function getNextTokens(m: (string | undefined)[]): Tokens | null {
	const fourMatch = m[5];
	if (!fourMatch) return null;
	return fourMatch.split(" ").filter(Boolean);
}

function getNextClasses(m: (string | undefined)[]): TokenClasses | null {
	const validMatch = m[6] || m[7];
	if (!validMatch) return null;
	return getClasses(validMatch);
}

function processEasyReadingRule(
	key: string,
	value: string,
): TransliterationRule | null {
	const match = easyReadingRuleRegex.exec(key);
	if (!match) return null;

	const prevClasses = getPrevClasses(match);
	const prevTokens = getPrevTokens(match);
	const tokens = getTokens(match) ?? [];
	const nextTokens = getNextTokens(match);
	const nextClasses = getNextClasses(match);

	const rule: TransliterationRule = {
		production: value,
		tokens,
		...(prevClasses && { prev_classes: prevClasses }),
		...(prevTokens && { prev_tokens: prevTokens }),
		...(nextTokens && { next_tokens: nextTokens }),
		...(nextClasses && { next_classes: nextClasses }),
		cost: 0,
	};

	rule.cost = costOf(rule);
	return rule;
}

function processEasyReadingOnMatchRules(
	eromr: Record<string, string>[],
): OnMatchRules {
	const rules: OnMatchRules = [];
	for (const dict of eromr) {
		for (const [key, production] of Object.entries(dict)) {
			const match = easyReadingOnMatchRuleRegex.exec(key);
			if (match?.[1] && match[2]) {
				rules.push({
					prev_classes: getClasses(match[1]),
					next_classes: getClasses(match[2]),
					production,
				});
			}
		}
	}
	return rules;
}

export function fromEasyReadingSettings(
	settings: EasyReadingSettings,
): GraphTransliteratorConfig {
	const rules: TransliterationRules = [];
	for (const [key, value] of Object.entries(settings.rules)) {
		const rule = processEasyReadingRule(key, value);
		if (rule) rules.push(rule);
	}

	return {
		tokens: settings.tokens,
		whitespace: settings.whitespace,
		onMatchRules: settings.onmatch_rules
			? processEasyReadingOnMatchRules(settings.onmatch_rules)
			: undefined,
		rules,
		metadata: settings.metadata,
	};
}

export function fromEasyReadingYaml(yamlString: string): GraphTransliterator {
	if (!yamlString?.trim()) {
		throw new Error(
			"YAML string is empty. Make sure the file was loaded correctly.",
		);
	}

	const raw = yaml.parse(yamlString) as
		| RawEasyReadingSettings
		| undefined
		| null;

	if (!raw || typeof raw !== "object") {
		throw new Error("YAML parsed to an empty or invalid object.");
	}

	if (!raw.tokens || !raw.rules || !raw.whitespace) {
		throw new Error(
			"Invalid YAML structure: missing required EasyReadingSettings fields (tokens, rules, or whitespace).",
		);
	}

	const settings: EasyReadingSettings = {
		tokens: raw.tokens,
		rules: raw.rules,
		onmatch_rules: raw.onmatch_rules,
		whitespace: {
			consolidate: raw.whitespace.consolidate,
			default: raw.whitespace.default,
			tokenClass: raw.whitespace.token_class,
		},
		metadata: raw.metadata,
	};

	const config = fromEasyReadingSettings(settings);
	return graphTransliterator(config);
}

function tokensByClassOf(
	tokenDict: Record<Token, TokenClasses>,
): TokensByClass {
	const tbc: TokensByClass = new Map();
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

function tokenizerPatternStrFrom(tkns: Token[]): string {
	const sorted = [...tkns].sort((a, b) => {
		if (b.length !== a.length) {
			return b.length - a.length;
		}
		return a < b ? -1 : a > b ? 1 : 0;
	});
	return `^(?:${sorted.map(escapeRegex).join("|")})`;
}

function tokenizerPatternFrom(tkns: Token[]): RegExp {
	return new RegExp(tokenizerPatternStrFrom(tkns));
}

function addRuleToken(
	token: Token,
	graph: GTGraph,
	parentId: NodeId,
	rule: TransliterationRule,
): { nodeId: NodeId; rule: TransliterationRule } {
	const children = graph.childrenOfType
		? graph.childrenOfType(parentId, "TokenNode")
		: [];

	let tokenNodeId: NodeId | undefined;
	for (const childId of children) {
		const node = graph.getNode(childId);
		if (node?.data.type === "TokenData" && node.data.token === token) {
			tokenNodeId = childId;
			break;
		}
	}

	let edge: GTEdge | undefined;
	if (tokenNodeId !== undefined) {
		edge = graph.getEdge(parentId, tokenNodeId);
	} else {
		const newNodeId = graph.addNode(
			{ type: "TokenData", token },
			token,
			token,
			"TokenNode",
		);
		graph.addEdge(parentId, newNodeId, { cost: rule.cost });
		return { nodeId: newNodeId, rule };
	}

	if (edge) {
		const newCost = Math.min(edge.data.cost ?? Infinity, rule.cost);
		if (graph.updateEdgeData) {
			graph.updateEdgeData(parentId, edge.target, { cost: newCost });
		} else {
			edge.data.cost = newCost;
		}
		return { nodeId: edge.target, rule };
	}

	return { nodeId: parentId, rule };
}

function graphFromRules(rules: TransliterationRules): GTGraph {
	const currentGraph = new DirectedGraph() as unknown as GTGraph;

	const rootId = currentGraph.addNode(
		{ type: "NoNodeData" },
		"^",
		"Start",
		"StartNode",
	);

	rules.forEach((rule, ruleId) => {
		let lastTokenNodeId = rootId;
		for (const token of rule.tokens) {
			const res = addRuleToken(token, currentGraph, lastTokenNodeId, rule);
			lastTokenNodeId = res.nodeId;
		}

		const ruleNodeId = currentGraph.addNode(
			{ type: "RuleData", ruleId },
			"",
			`Rule #${ruleId}`,
			"RuleNode",
		);
		currentGraph.addEdge(lastTokenNodeId, ruleNodeId, { cost: rule.cost });
	});

	return currentGraph;
}

function generateOnMatchRulesLookup(
	tokenClasses: Record<Token, TokenClasses>,
	ruleSetList: OnMatchRules,
): OnMatchRulesLookup {
	const tbc = tokensByClassOf(tokenClasses);
	const lookup: OnMatchRulesLookup = new Map();

	ruleSetList.forEach((rule, ruleId) => {
		const nextClass = rule.next_classes[0];
		const prevClass = rule.prev_classes[rule.prev_classes.length - 1];

		if (nextClass && prevClass) {
			const currTokens = tbc.get(nextClass) ?? new Set();
			const prevTokens = tbc.get(prevClass) ?? new Set();

			for (const currT of currTokens) {
				if (!lookup.has(currT)) lookup.set(currT, new Map());
				const prevMap = lookup.get(currT)!;

				for (const prevT of prevTokens) {
					if (!prevMap.has(prevT)) prevMap.set(prevT, []);
					prevMap.get(prevT)!.push(ruleId);
				}
			}
		}
	});

	return lookup;
}

export function graphTransliterator(
	config: GraphTransliteratorConfig,
): GraphTransliterator {
	const onlyTokens = Object.keys(config.tokens);
	const resolvedOnMatchRules = config.onMatchRules ?? config.onmatch_rules;
	return new GraphTransliterator({
		tokens: config.tokens,
		rules: config.rules,
		whitespace: config.whitespace,
		metadata: config.metadata,
		onMatchRules: resolvedOnMatchRules,
		onMatchRulesLookup: resolvedOnMatchRules
			? generateOnMatchRulesLookup(config.tokens, resolvedOnMatchRules)
			: undefined,
		tokensByClass: tokensByClassOf(config.tokens),
		tokenizerPattern: tokenizerPatternFrom(onlyTokens),
		tokenizerPatternStr: tokenizerPatternStrFrom(onlyTokens),
		graph: graphFromRules(config.rules),
	});
}

export function rulesOf(gt: GraphTransliterator): TransliterationRules {
	return gt.rules;
}

export function productionOfRule(
	ruleId: RuleId,
	gt: GraphTransliterator,
): Production | undefined {
	return gt.rules[ruleId]?.production;
}

export function tokensOfRule(
	ruleId: RuleId,
	gt: GraphTransliterator,
): Tokens | undefined {
	return gt.rules[ruleId]?.tokens;
}

export function* productionsOf(gt: GraphTransliterator): Generator<Production> {
	for (const rule of gt.rules) {
		if (rule) yield rule.production;
	}
}

export function tokenize(input: string, gt: GraphTransliterator): Tokens {
	const tokens: Tokens = [gt.whiteSpace.default];
	let matchAt = 0;

	const isWhitespace = (tok: string): boolean => {
		return gt.tokens[tok]?.includes(gt.whiteSpace.tokenClass) ?? false;
	};

	let prevWhitespace = true;

	while (matchAt < input.length) {
		const remaining = input.slice(matchAt);
		const match = gt.tokenizerPattern.exec(remaining);
		if (!match) {
			matchAt++;
		} else {
			matchAt += match[0].length;
			const token = match[0];
			if (isWhitespace(token)) {
				if (prevWhitespace && gt.whiteSpace.consolidate) {
					continue;
				} else {
					prevWhitespace = true;
				}
			} else {
				prevWhitespace = false;
			}
			tokens.push(token);
		}
	}

	if (gt.whiteSpace.consolidate) {
		while (tokens.length > 1 && isWhitespace(tokens[tokens.length - 1])) {
			tokens.pop();
		}
	}

	tokens.push(gt.whiteSpace.default);
	return tokens;
}

function orderedOutgoing(
	nodeId: NodeId,
	currToken: Token | undefined,
	graph: GTGraph,
	gt: GraphTransliterator,
): { tokenEdges: GTEdge[]; ruleEdges: GTEdge[] } {
	const childrenEdges: GTEdge[] = Array.from(graph.edges.values()).filter(
		(e: GTEdge) => e.source === nodeId,
	);

	childrenEdges.sort((a: GTEdge, b: GTEdge) => {
		const costA = a.data?.cost ?? 0;
		const costB = b.data?.cost ?? 0;
		if (costA !== costB) {
			return costA - costB;
		}
		const nodeA = graph.getNode(a.target);
		const nodeB = graph.getNode(b.target);
		if (nodeA?.type === "RuleNode" && nodeB?.type === "RuleNode") {
			const ruleA =
				gt.rules[nodeA.data.type === "RuleData" ? nodeA.data.ruleId : -1];
			const ruleB =
				gt.rules[nodeB.data.type === "RuleData" ? nodeB.data.ruleId : -1];
			if (ruleA && ruleB) {
				const scoreA =
					(ruleA.prev_tokens?.length ?? 0) +
					(ruleA.next_tokens?.length ?? 0) +
					(ruleA.prev_classes?.length ?? 0) +
					(ruleA.next_classes?.length ?? 0);
				const scoreB =
					(ruleB.prev_tokens?.length ?? 0) +
					(ruleB.next_tokens?.length ?? 0) +
					(ruleB.prev_classes?.length ?? 0) +
					(ruleB.next_classes?.length ?? 0);
				return scoreB - scoreA;
			}
		}
		return 0;
	});

	const tokenEdges: GTEdge[] = [];
	const ruleEdges: GTEdge[] = [];

	for (const e of childrenEdges) {
		const tailNode = graph.getNode(e.target);
		if (
			tailNode?.type === "TokenNode" &&
			tailNode.data.type === "TokenData" &&
			tailNode.data.token === currToken
		) {
			tokenEdges.push(e);
		} else if (tailNode?.type === "RuleNode") {
			ruleEdges.push(e);
		}
	}

	return { tokenEdges, ruleEdges };
}

function tokenInClass(
	token: Token | undefined,
	tokenClass: TokenClass | undefined,
	tokensByClass: TokensByClass,
): boolean {
	if (token === undefined || tokenClass === undefined) return false;
	return tokensByClass.get(tokenClass)?.has(token) ?? false;
}

function matchConstraints(
	node: GTNode,
	tokenIdx: number,
	tIdx: number,
	tokens: Tokens,
	gt: GraphTransliterator,
): boolean {
	if (node.data.type !== "RuleData") return false;
	const rule = gt.rules[node.data.ruleId];
	if (!rule) return false;

	if (rule.prev_tokens) {
		const startIdx = tokenIdx - rule.prev_tokens.length;
		if (startIdx < 0) return false;
		for (let i = 0; i < rule.prev_tokens.length; i++) {
			if (tokens[startIdx + i] !== rule.prev_tokens[i]) return false;
		}
	}

	if (rule.next_tokens) {
		const startIdx = tIdx;
		if (startIdx + rule.next_tokens.length > tokens.length) return false;
		for (let i = 0; i < rule.next_tokens.length; i++) {
			if (tokens[startIdx + i] !== rule.next_tokens[i]) return false;
		}
	}

	if (rule.prev_classes) {
		const startIdx =
			tokenIdx - (rule.prev_tokens?.length ?? 0) - rule.prev_classes.length;
		if (startIdx < 0) return false;
		for (let i = 0; i < rule.prev_classes.length; i++) {
			if (
				!tokenInClass(
					tokens[startIdx + i],
					rule.prev_classes[i],
					gt.tokensByClass,
				)
			) {
				return false;
			}
		}
	}

	if (rule.next_classes) {
		const nextTokensLen = rule.next_tokens ? rule.next_tokens.length : 0;
		const startIdx = tIdx + nextTokensLen;

		if (startIdx + rule.next_classes.length > tokens.length) return false;
		for (let i = 0; i < rule.next_classes.length; i++) {
			if (
				!tokenInClass(
					tokens[startIdx + i],
					rule.next_classes[i],
					gt.tokensByClass,
				)
			) {
				return false;
			}
		}
	}

	return true;
}

function matchOnMatchRuleAt(
	ruleIdx: number,
	tokenIdx: number,
	tokens: Tokens,
	gt: GraphTransliterator,
): boolean {
	const rule = gt.onMatchRules?.[ruleIdx];
	if (!rule) return true;

	if (rule.prev_classes) {
		const startIdx = tokenIdx - rule.prev_classes.length;
		if (startIdx < 0) return false;
		for (let i = 0; i < rule.prev_classes.length; i++) {
			if (
				!tokenInClass(
					tokens[startIdx + i],
					rule.prev_classes[i],
					gt.tokensByClass,
				)
			) {
				return false;
			}
		}
	}

	if (rule.next_classes) {
		if (tokenIdx + rule.next_classes.length > tokens.length) return false;
		for (let i = 0; i < rule.next_classes.length; i++) {
			if (
				!tokenInClass(
					tokens[tokenIdx + i],
					rule.next_classes[i],
					gt.tokensByClass,
				)
			) {
				return false;
			}
		}
	}

	return true;
}

export function matchRulesAt(
	tokenIdx: number,
	tokens: Tokens,
	gt: GraphTransliterator,
): MatchesAtResults {
	const stack: { tIdx: number; nodeId: NodeId }[] = [];
	const matches: MatchesAtResults = [];

	const addOutgoingToStack = (tIdx: number, nId: NodeId) => {
		const { tokenEdges, ruleEdges } = orderedOutgoing(
			nId,
			tokens[tIdx],
			gt.graph,
			gt,
		);

		for (let i = ruleEdges.length - 1; i >= 0; i--) {
			stack.push({ tIdx, nodeId: ruleEdges[i].target });
		}
		for (let i = tokenEdges.length - 1; i >= 0; i--) {
			stack.push({ tIdx: tIdx + 1, nodeId: tokenEdges[i].target });
		}
	};

	addOutgoingToStack(tokenIdx, 0);

	while (stack.length > 0) {
		const { tIdx, nodeId } = stack.pop()!;
		const node = gt.graph.getNode(nodeId);
		if (!node) continue;

		if (node.type === "RuleNode") {
			if (matchConstraints(node, tokenIdx, tIdx, tokens, gt)) {
				if (node.data.type === "RuleData") {
					matches.push(node.data.ruleId);
				}
			}
		} else {
			addOutgoingToStack(tIdx, nodeId);
		}
	}

	return matches;
}

function matchRuleAt(
	tokenIdx: number,
	tokens: Tokens,
	gt: GraphTransliterator,
): MatchAtResult {
	const stack: { tIdx: number; nodeId: NodeId }[] = [];

	const addOutgoingToStack = (tIdx: number, nId: NodeId) => {
		const { tokenEdges, ruleEdges } = orderedOutgoing(
			nId,
			tokens[tIdx],
			gt.graph,
			gt,
		);

		for (let i = ruleEdges.length - 1; i >= 0; i--) {
			stack.push({ tIdx, nodeId: ruleEdges[i].target });
		}
		for (let i = tokenEdges.length - 1; i >= 0; i--) {
			stack.push({ tIdx: tIdx + 1, nodeId: tokenEdges[i].target });
		}
	};

	addOutgoingToStack(tokenIdx, 0);

	while (stack.length > 0) {
		const { tIdx, nodeId } = stack.pop()!;
		const node = gt.graph.getNode(nodeId);
		if (!node) continue;

		if (
			node.type === "RuleNode" &&
			matchConstraints(node, tokenIdx, tIdx, tokens, gt)
		) {
			if (node.data.type === "RuleData") {
				return { type: "RuleIdx", ruleId: node.data.ruleId };
			}
		} else {
			addOutgoingToStack(tIdx, nodeId);
		}
	}

	return { type: "None" };
}

export function transliterate(input: string, gt: GraphTransliterator): string {
	const tokens = tokenize(input, gt);
	const numTokens = tokens.length;

	let output = "";
	let tokenIdx = 1;

	while (tokenIdx < numTokens - 1) {
		const matchedRule = matchRuleAt(tokenIdx, tokens, gt);

		if (matchedRule.type === "None") {
			tokenIdx++;
			continue;
		}

		const ruleId = matchedRule.ruleId;
		const currToken = tokens[tokenIdx];
		const prevToken = tokens[tokenIdx - 1];

		let omrProduction = "";
		if (gt.onMatchRulesLookup && gt.onMatchRules) {
			const applicableOmrIds = gt.onMatchRulesLookup
				.get(currToken)
				?.get(prevToken);
			if (applicableOmrIds) {
				const validOmrId = applicableOmrIds.find((id) =>
					matchOnMatchRuleAt(id, tokenIdx, tokens, gt),
				);
				if (validOmrId !== undefined) {
					omrProduction = gt.onMatchRules[validOmrId].production;
				}
			}
		}

		const rule = gt.rules[ruleId];
		output += omrProduction + (rule?.production ?? "");
		tokenIdx += Math.max(1, rule?.tokens.length ?? 1);
	}

	return output;
}

export function transliterateReporting(
	input: string,
	gt: GraphTransliterator,
): TransliterationReport {
	const tokens = tokenize(input, gt);
	const numTokens = tokens.length;

	const output: TransliterationReport = [];
	let tokenIdx = 1;

	while (tokenIdx < numTokens - 1) {
		const matchedRule = matchRuleAt(tokenIdx, tokens, gt);

		if (matchedRule.type === "None") {
			tokenIdx++;
			continue;
		}

		const ruleId = matchedRule.ruleId;
		const rule = gt.rules[ruleId];

		if (rule) {
			output.push({
				type: "RuleProduction",
				tokenIdx,
				ruleId,
				tokens: rule.tokens,
				production: rule.production,
			});
			tokenIdx += Math.max(1, rule.tokens.length);
		} else {
			tokenIdx++;
		}
	}

	return output;
}

export function allMatchesAt(
	tokenIdx: number,
	tokens: Tokens,
	gt: GraphTransliterator,
): MatchesAtResults {
	return matchRulesAt(tokenIdx, tokens, gt);
}
