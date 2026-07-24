import { DirectedGraph } from "./Graphs.js";
import {
    Token,
    TokenClass,
    RawRuleDict,
    RawOnMatchDict,
    RawWhitespaceDict,
    TransliterationRule,
    OnMatchRule,
    WhitespaceRules,
    ConstraintDict,
    Node,
    Edge,
} from "./types.js";

// ---------- initialize tokens ----------

/** Generates lookup table of tokens in each class. */
export function tokensByClassOf(
    tokens: Record<Token, TokenClass[] | Set<TokenClass>>,
): Map<TokenClass, Set<Token>> {
    const out = new Map<TokenClass, Set<Token>>();

    for (const [token, tokenClasses] of Object.entries(tokens)) {
        for (const tokenClass of tokenClasses) {
            if (!out.has(tokenClass)) {
                out.set(tokenClass, new Set<Token>());
            }
            out.get(tokenClass)!.add(token);
        }
    }

    return out;
}

// ---------- initialize rules ----------

/** Calculate total number of constrained and matched tokens in a rule. */
export function numTokensOf(rule: RawRuleDict): number {
    let total = rule.tokens?.length ?? 0;

    const optionalFields = [
        rule.prev_classes,
        rule.prev_tokens,
        rule.next_tokens,
        rule.next_classes,
    ];

    for (const field of optionalFields) {
        if (field) {
            total += field.length;
        }
    }

    return total;
}

/**
 * Calculate cost of a rule based on the number of constraints.
 * Formula: log2(1 + 1 / (1 + num_tokens))
 */
export function costOf(rule: RawRuleDict): number {
    return Math.log2(1 + 1 / (1 + numTokensOf(rule)));
}

/** Converts rule dict into a TransliterationRule object. */
export function transliterationRuleOf(rule: RawRuleDict): TransliterationRule {
    return {
        production: rule.production ?? "",
        prev_classes: rule.prev_classes,
        prev_tokens: rule.prev_tokens,
        tokens: rule.tokens ?? [],
        next_tokens: rule.next_tokens,
        next_classes: rule.next_classes,
        cost: rule.cost ?? costOf(rule),
    };
}

// ---------- initialize onmatch rules ----------

/** Converts raw dict into OnMatchRule. */
export function onMatchRuleOf(onmatchRule: RawOnMatchDict): OnMatchRule {
    return {
        prev_classes: onmatchRule.prev_classes,
        next_classes: onmatchRule.next_classes,
        production: onmatchRule.production,
    };
}

/** Creates a dict lookup from current to previous token. */
export function onMatchRulesLookup(
    tokens: Record<Token, TokenClass[] | Set<TokenClass>>,
    onmatchRules: OnMatchRule[],
): Record<Token, Record<Token, number[]>> {
    const onmatchLookup: Record<Token, Record<Token, number[]>> = {};

    onmatchRules.forEach((rule, ruleIdx) => {
        for (const [tokenKey, tokenClasses] of Object.entries(tokens)) {
            const classesSet = new Set(tokenClasses);
            if (classesSet.has(rule.next_classes[0])) {
                for (const [prevTokenKey, prevTokenClasses] of Object.entries(
                    tokens,
                )) {
                    const prevClassesSet = new Set(prevTokenClasses);
                    if (
                        prevClassesSet.has(
                            rule.prev_classes[rule.prev_classes.length - 1],
                        )
                    ) {
                        if (!onmatchLookup[tokenKey]) {
                            onmatchLookup[tokenKey] = {};
                        }
                        if (!onmatchLookup[tokenKey][prevTokenKey]) {
                            onmatchLookup[tokenKey][prevTokenKey] = [];
                        }
                        onmatchLookup[tokenKey][prevTokenKey].push(ruleIdx);
                    }
                }
            }
        }
    });

    return onmatchLookup;
}

// ---------- initialize whitespace ----------

/** Converts raw whitespace object into WhitespaceRules. */
export function whitespaceRulesOf(
    whitespace: RawWhitespaceDict,
): WhitespaceRules {
    return {
        default: whitespace.default,
        token_class: whitespace.token_class,
        consolidate: whitespace.consolidate,
    };
}

// ---------- initialize tokenizer ----------

/** Generates regular expression tokenizer pattern from token list. */
export function tokenizerPatternFrom(tokens: Token[]): RegExp {
    const sortedTokens = [...tokens].sort((a, b) => {
        if (a.length !== b.length) {
            return b.length - a.length; // Longest first
        }
        return b.localeCompare(a);
    });

    const escapeRegex = (str: string) =>
        str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regexStr = "(" + sortedTokens.map(escapeRegex).join("|") + ")";
    return new RegExp(regexStr, "g");
}

// ---------- initialize graph ----------

/** Generates a parsing graph from the given rules. */
export function graphFrom(rules: TransliterationRule[]): DirectedGraph {
    const graph = new DirectedGraph();

    // Root start node
    graph.addNode({ type: "Start" });

    rules.forEach((rule, ruleKey) => {
        let parentKey = 0;

        for (const token of rule.tokens) {
            const parentNode = graph.nodes[parentKey];
            parentNode.token_children = parentNode.token_children || {};

            let tokenNodeKey = parentNode.token_children[token];

            if (tokenNodeKey === undefined) {
                tokenNodeKey = graph.nodes.length;
                graph.addNode({ type: "token", token });
                graph.addEdge(parentKey, tokenNodeKey, { token });
                parentNode.token_children[token] = tokenNodeKey;
            }

            const currEdge = graph.getEdge(parentKey, tokenNodeKey)!;
            const currCost = currEdge.cost ?? 1.0;
            if (currCost > rule.cost) {
                currEdge.cost = rule.cost;
            }

            parentKey = tokenNodeKey;
        }

        const ruleNodeKey = graph.nodes.length;
        graph.addNode({ type: "rule", rule_key: ruleKey, accepting: true });

        const parentNode = graph.nodes[parentKey];
        parentNode.rule_children = parentNode.rule_children || [];
        parentNode.rule_children.push(ruleNodeKey);
        parentNode.rule_children.sort(
            (a, b) =>
                rules[graph.nodes[a].rule_key!].cost -
                rules[graph.nodes[b].rule_key!].cost,
        );

        const edgeData: Edge = { cost: rule.cost };

        const hasConstraints = Boolean(
            rule.prev_classes ||
            rule.prev_tokens ||
            rule.next_tokens ||
            rule.next_classes,
        );

        if (hasConstraints) {
            const constraints: ConstraintDict = {};
            if (rule.prev_classes) constraints.prev_classes = rule.prev_classes;
            if (rule.prev_tokens) constraints.prev_tokens = rule.prev_tokens;
            if (rule.next_tokens) constraints.next_tokens = rule.next_tokens;
            if (rule.next_classes) constraints.next_classes = rule.next_classes;
            edgeData.constraints = constraints;
        }

        graph.addEdge(parentKey, ruleNodeKey, edgeData);
    });

    // Post-process ordered_children for quick matching execution
    graph.nodes.forEach((node, nodeKey) => {
        const orderedChildren: Record<string, number[]> = {};
        const ruleChildrenKeys = node.rule_children;

        if (ruleChildrenKeys) {
            orderedChildren["__rules__"] = [...ruleChildrenKeys].sort(
                (a, b) =>
                    rules[graph.nodes[a].rule_key!].cost -
                    rules[graph.nodes[b].rule_key!].cost,
            );
            delete node.rule_children;
        }

        if (node.token_children) {
            for (const [token, tokenKey] of Object.entries(
                node.token_children,
            )) {
                orderedChildren[token] = [tokenKey];

                if (ruleChildrenKeys) {
                    orderedChildren[token].push(...ruleChildrenKeys);
                }

                orderedChildren[token].sort(
                    (a, b) =>
                        graph.getEdge(nodeKey, a)!.cost! -
                        graph.getEdge(nodeKey, b)!.cost!,
                );
            }
            delete node.token_children;
        }

        node.ordered_children = orderedChildren;
    });

    return graph;
}
