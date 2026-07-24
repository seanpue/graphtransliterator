// src/GraphTransliterator.ts
/**
 * @module GraphTransliterator
 * A high-performance string matching and deterministic token transformation graph framework.
 * This TypeScript module is an implementation based on the following academic work:[cite: 3]
 *
 * @citation
 * Pue, A. S. (2019). Graph Transliterator: A graph-based transliteration tool.
 * Journal of Open Source Software, 4(44), 1717. https://doi.org/10.21105/joss.01717[cite: 3]
 *
 * @description
 * This module parses complex script transformation schemas (e.g., EasyReading settings)[cite: 3]
 * and maps character match combinations into optimized Directed Acyclic Word Graphs (DAWGs)[cite: 3]
 * or Finite State Transducers (FSTs). It features deterministic lookup engines,[cite: 3]
 * context-aware rule validation (lookbehinds/lookarounds), and dynamic whitespace consolidation.[cite: 3]
 */
// src/GraphTransliterator.ts
/**
 * @module GraphTransliterator
 * A high-performance string matching and deterministic token transformation graph framework.
 *
 * @citation
 * Pue, A. S. (2019). Graph Transliterator: A graph-based transliteration tool.
 * Journal of Open Source Software, 4(44), 1717. https://doi.org/10.21105/joss.01717[cite: 3]
 */

import yaml from "yaml";
import {
    addEdge,
    addNode,
    childrenOfType,
    getEdge,
    getNode,
    initGraph,
    updateEdgeData,
} from "./Graphs.js";
//import { costOf } from "./Rules.js";
import {
    Cost,
    DirectedGraph,
    EasyReadingSettings,
    Edge,
    GraphTransliteratorConfig,
    GTEdge,
    GTEdgeDataType,
    GTGraph,
    GTNode,
    GTNodeDataType,
    GTNodeType,
    MatchAtResult,
    MatchesAtResults,
    Metadata,
    Node,
    NodeId,
    OnMatchRuleIds,
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
    TransliterationProduction,
    TransliterationReport,
    TransliterationRule,
    TransliterationRules,
    WhitespaceRule,
} from "./types.js";

// =============================================================================
// COMPILED OPERATIONAL TRANSLITERATOR CONTEXT
// =============================================================================

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
        whiteSpace: WhitespaceRule;
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
        this.whiteSpace = config.whiteSpace;
        this.onMatchRules = config.onMatchRules;
        this.metadata = config.metadata;
        this.onMatchRulesLookup = config.onMatchRulesLookup;
        this.tokensByClass = config.tokensByClass;
        this.tokenizerPattern = config.tokenizerPattern;
        this.tokenizerPatternStr = config.tokenizerPatternStr;
        this.graph = config.graph;
    }

    /**
     * Returns a new GraphTransliterator instance with rules filtered out
     * based on their production outputs.
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
            whitespaceRule: this.whiteSpace,
            onMatchRules: this.onMatchRules,
            metadata: this.metadata,
        });
    }
}

// =============================================================================
// INTERNAL RECONNAISSANCE REGEX PATTERNS
// =============================================================================

const easyReadingRuleRegex =
    /^(?:\(((?:\s?<.+?>\s+)+)?(.+?)\s?\) |((?:\s?<.+?>\s+)+)?)?((?:\n|\r|.)+?)(?:\s+(?:\((.+?)((?:\s+<.+?>?)?)\)$)|((?:\s+<.+?>)+)|$)/;

const classesRegex = /<(.+?)>/g;
const easyReadingOnMatchRuleRegex =
    /^((?:<[^+<\s]+>\s*)+)\+((?:\s*<[^+<]+>)+)\s*$/;

// =============================================================================
// SCHEMA SANITIZATION METRIC UTILITIES
// =============================================================================

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

    return {
        production: value,
        prevClasses,
        prevTokens,
        tokens,
        nextTokens,
        nextClasses,
        cost: costOf(prevClasses, prevTokens, tokens, nextTokens, nextClasses),
    };
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
                    prevClasses: getClasses(match[1]),
                    nextClasses: getClasses(match[2]),
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
        whitespaceRule: settings.whitespace,
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

// =============================================================================
// COMPILATION LOOKUP CORE DYNAMICS
// =============================================================================

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
    const sorted = [...tkns].sort(
        (a, b) => b.length - a.length || a.localeCompare(b),
    );
    return `^(?:${sorted.map(escapeRegex).join("|")})`;
}

function tokenizerPatternFrom(tkns: Token[]): RegExp {
    return new RegExp(tokenizerPatternStrFrom(tkns));
}

// =============================================================================
// ALGORITHMIC VERTEX STRUCTURE COMPILATION
// =============================================================================

const startNode: GTNode = {
    id: 0,
    token: "^",
    type: "StartNode",
    label: "Start",
    data: { type: "NoNodeData" },
};

function addRuleToken(
    token: Token,
    graph: GTGraph,
    parentId: NodeId,
    rule: TransliterationRule,
): { graph: GTGraph; nodeId: NodeId; rule: TransliterationRule } {
    let currentGraph = graph;
    const children = childrenOfType(currentGraph, parentId, "TokenNode");

    let tokenNodeId: NodeId | undefined;
    for (const childId of children) {
        const node = getNode(currentGraph, childId);
        if (node?.data.type === "TokenData" && node.data.token === token) {
            tokenNodeId = childId;
            break;
        }
    }

    let edge: GTEdge | undefined;
    if (tokenNodeId !== undefined) {
        edge = getEdge(currentGraph, parentId, tokenNodeId);
    } else {
        let newNode: GTNode;
        [currentGraph, newNode] = addNode(
            currentGraph,
            token,
            "TokenNode",
            token,
            {
                type: "TokenData",
                token,
            },
        );
        let newEdge: GTEdge;
        [currentGraph, newEdge] = addEdge(currentGraph, parentId, newNode.id, {
            cost: rule.cost,
        });
        edge = newEdge;
    }

    if (edge) {
        const newCost = Math.min(edge.data.cost, rule.cost);
        currentGraph = updateEdgeData(currentGraph, parentId, edge.target, {
            cost: newCost,
        });
        return { graph: currentGraph, nodeId: edge.target, rule };
    }

    return { graph: currentGraph, nodeId: parentId, rule };
}

function graphFromRules(rules: TransliterationRules): GTGraph {
    let currentGraph = initGraph<GTNodeType, GTNodeDataType, GTEdgeDataType>(
        [startNode],
        new Map(),
    );

    rules.forEach((rule, ruleId) => {
        let lastTokenNodeId = 0;
        for (const token of rule.tokens) {
            const res = addRuleToken(
                token,
                currentGraph,
                lastTokenNodeId,
                rule,
            );
            currentGraph = res.graph;
            lastTokenNodeId = res.nodeId;
        }

        let ruleNode: GTNode;
        [currentGraph, ruleNode] = addNode(
            currentGraph,
            "",
            "RuleNode",
            `Rule #${ruleId}`,
            {
                type: "RuleData",
                ruleId,
            },
        );
        [currentGraph] = addEdge(currentGraph, lastTokenNodeId, ruleNode.id, {
            cost: rule.cost,
        });
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
        const nextClass = rule.nextClasses[0];
        const prevClass = rule.prevClasses[rule.prevClasses.length - 1];

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
    return new GraphTransliterator({
        tokens: config.tokens,
        rules: config.rules,
        whiteSpace: config.whitespaceRule,
        metadata: config.metadata,
        onMatchRules: config.onMatchRules,
        onMatchRulesLookup: config.onMatchRules
            ? generateOnMatchRulesLookup(config.tokens, config.onMatchRules)
            : undefined,
        tokensByClass: tokensByClassOf(config.tokens),
        tokenizerPattern: tokenizerPatternFrom(onlyTokens),
        tokenizerPatternStr: tokenizerPatternStrFrom(onlyTokens),
        graph: graphFromRules(config.rules),
    });
}

// =============================================================================
// REFLECTION ACCESS UTILITIES
// =============================================================================

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

// =============================================================================
// RUNTIME LOOKUP & TRANSLITERATION ENGINE
// =============================================================================

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
    const childrenEdges = Array.from(graph.edges.values()).filter(
        (e) => e.source === nodeId,
    );

    childrenEdges.sort((a, b) => {
        if (a.data.cost !== b.data.cost) {
            return a.data.cost - b.data.cost;
        }
        const nodeA = getNode(graph, a.target);
        const nodeB = getNode(graph, b.target);
        if (nodeA?.type === "RuleNode" && nodeB?.type === "RuleNode") {
            const ruleA =
                gt.rules[
                    nodeA.data.type === "RuleData" ? nodeA.data.ruleId : -1
                ];
            const ruleB =
                gt.rules[
                    nodeB.data.type === "RuleData" ? nodeB.data.ruleId : -1
                ];
            if (ruleA && ruleB) {
                const scoreA =
                    (ruleA.prevTokens?.length ?? 0) +
                    (ruleA.nextTokens?.length ?? 0) +
                    (ruleA.prevClasses?.length ?? 0) +
                    (ruleA.nextClasses?.length ?? 0);
                const scoreB =
                    (ruleB.prevTokens?.length ?? 0) +
                    (ruleB.nextTokens?.length ?? 0) +
                    (ruleB.prevClasses?.length ?? 0) +
                    (ruleB.nextClasses?.length ?? 0);
                return scoreB - scoreA;
            }
        }
        return 0;
    });

    const tokenEdges: GTEdge[] = [];
    const ruleEdges: GTEdge[] = [];

    for (const e of childrenEdges) {
        const tailNode = getNode(graph, e.target);
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

    // 1. Prev Tokens Lookbehind
    if (rule.prevTokens) {
        const startIdx = tokenIdx - rule.prevTokens.length;
        if (startIdx < 0) return false;
        for (let i = 0; i < rule.prevTokens.length; i++) {
            if (tokens[startIdx + i] !== rule.prevTokens[i]) return false;
        }
    }

    // 2. Next Tokens Lookahead
    if (rule.nextTokens) {
        const startIdx = tIdx;
        if (startIdx + rule.nextTokens.length > tokens.length) return false;
        for (let i = 0; i < rule.nextTokens.length; i++) {
            if (tokens[startIdx + i] !== rule.nextTokens[i]) return false;
        }
    }

    // 3. Prev Classes Lookbehind
    if (rule.prevClasses) {
        const startIdx =
            tokenIdx - (rule.prevTokens?.length ?? 0) - rule.prevClasses.length;
        if (startIdx < 0) return false;
        for (let i = 0; i < rule.prevClasses.length; i++) {
            if (
                !tokenInClass(
                    tokens[startIdx + i],
                    rule.prevClasses[i],
                    gt.tokensByClass,
                )
            ) {
                return false;
            }
        }
    }

    // 4. Next Classes Lookahead
    if (rule.nextClasses) {
        const nextTokensLen = rule.nextTokens ? rule.nextTokens.length : 0;
        const startIdx = tIdx + nextTokensLen;

        if (startIdx + rule.nextClasses.length > tokens.length) return false;
        for (let i = 0; i < rule.nextClasses.length; i++) {
            if (
                !tokenInClass(
                    tokens[startIdx + i],
                    rule.nextClasses[i],
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

    if (rule.prevClasses) {
        const startIdx = tokenIdx - rule.prevClasses.length;
        if (startIdx < 0) return false;
        for (let i = 0; i < rule.prevClasses.length; i++) {
            if (
                !tokenInClass(
                    tokens[startIdx + i],
                    rule.prevClasses[i],
                    gt.tokensByClass,
                )
            ) {
                return false;
            }
        }
    }

    if (rule.nextClasses) {
        if (tokenIdx + rule.nextClasses.length > tokens.length) return false;
        for (let i = 0; i < rule.nextClasses.length; i++) {
            if (
                !tokenInClass(
                    tokens[tokenIdx + i],
                    rule.nextClasses[i],
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
        const node = getNode(gt.graph, nodeId);
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
        const node = getNode(gt.graph, nodeId);
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
