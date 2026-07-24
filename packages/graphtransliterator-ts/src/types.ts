// =============================================================================
// DOMAIN PRIMITIVES & IDENTIFIERS
// =============================================================================

export type Token = string;
export type Tokens = Token[];
export type TokenClass = string;
export type TokenClasses = TokenClass[];
export type Production = string;
export type Cost = number;

export type NodeId = number;
export type NodeLabel = string;
export type RuleId = number;
export type OnMatchRuleId = number;
export type OnMatchRuleIds = OnMatchRuleId[];

export type Metadata = Record<string, string>;
export type EdgeIdString = string;

// =============================================================================
// GENERIC GRAPH PARITY INTERFACES (Shared 1:1 with Python)
// =============================================================================

/**
 * Generic vertex representation matching Python Node[T, N].
 */
export interface Node<T, N> {
    id: NodeId;
    token: Token;
    type: T;
    label: NodeLabel;
    data: N;
}

/**
 * Generic edge representation matching Python Edge[E].
 */
export interface Edge<E> {
    source: NodeId;
    target: NodeId;
    data: E;
}

/**
 * Canonical JSON graph serialization shape.
 */
export interface LoadedGraphDict<T, N, E> {
    nodes: Node<T, N>[];
    edges: Edge<E>[];
}

// =============================================================================
// RULE DECLARATIONS
// =============================================================================

export interface TransliterationRule {
    production: Production;
    prevClasses?: TokenClasses | null;
    prevTokens?: Tokens | null;
    tokens: Tokens;
    nextTokens?: Tokens | null;
    nextClasses?: TokenClasses | null;
    cost: Cost;
}
export type TransliterationRules = TransliterationRule[];

export interface WhitespaceRule {
    consolidate: boolean;
    default: Token;
    tokenClass: TokenClass;
}

export interface OnMatchRule {
    prevClasses: TokenClasses;
    nextClasses: TokenClasses;
    production: Production;
}
export type OnMatchRules = OnMatchRule[];

// =============================================================================
// RAW SCHEMA CONFIGURATION INTERFACES
// =============================================================================

export interface RawWhitespaceRule {
    consolidate: boolean;
    default: string;
    token_class: string;
}

export interface RawEasyReadingSettings {
    tokens: Record<string, string[]>;
    rules: Record<string, string>;
    onmatch_rules?: Record<string, string>[];
    whitespace: RawWhitespaceRule;
    metadata?: Record<string, string>;
}

// =============================================================================
// SANITIZED INTERNAL CONFIGURATION SCHEMAS
// =============================================================================

export interface EasyReadingSettings {
    tokens: Record<Token, TokenClasses>;
    rules: Record<string, string>;
    onmatch_rules?: Record<string, string>[];
    whitespace: WhitespaceRule;
    metadata?: Metadata;
}

export interface GraphTransliteratorConfig {
    tokens: Record<Token, TokenClasses>;
    rules: TransliterationRules;
    whitespaceRule: WhitespaceRule;
    onMatchRules?: OnMatchRules;
    metadata?: Metadata;
}

// =============================================================================
// ENGINE SPECIFIC GRAPH & PROCESSOR TYPES
// =============================================================================

export type TokensByClass = Map<TokenClass, Set<Token>>;
export type OnMatchRulesLookup = Map<Token, Map<Token, OnMatchRuleIds>>;

export type GTNodeType = "StartNode" | "TokenNode" | "RuleNode";

export type GTNodeDataType =
    | { type: "NoNodeData" }
    | { type: "TokenData"; token: string }
    | { type: "RuleData"; ruleId: number };

export type GTEdgeDataType = { cost: Cost };

export type GTNode = Node<GTNodeType, GTNodeDataType>;
export type GTEdge = Edge<GTEdgeDataType>;

export type MatchAtResult =
    | { type: "None" }
    | { type: "RuleIdx"; ruleId: number };

export type MatchesAtResults = number[];

export type TransliterationProduction = {
    type: "RuleProduction";
    tokenIdx: number;
    ruleId: RuleId;
    tokens: Tokens;
    production: string;
};

export type TransliterationReport = TransliterationProduction[];
