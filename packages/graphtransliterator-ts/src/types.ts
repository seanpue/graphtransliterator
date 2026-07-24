// src/types.ts

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
	token: Token | null;
	type: T;
	label: NodeLabel | null;
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
	tokens: Tokens;
	cost: Cost;
	prev_classes?: TokenClasses | null;
	prev_tokens?: Tokens | null;
	next_tokens?: Tokens | null;
	next_classes?: TokenClasses | null;
}
export type TransliterationRules = TransliterationRule[];

export interface WhitespaceRule {
	consolidate: boolean;
	default: Token;
	tokenClass: TokenClass;
}

export interface OnMatchRule {
	prev_classes: TokenClasses;
	next_classes: TokenClasses;
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
	whitespace: WhitespaceRule;
	onMatchRules?: OnMatchRules;
	onmatch_rules?: OnMatchRules;
	metadata?: Metadata;
	onMatchRulesLookup?: OnMatchRulesLookup;
	onmatch_rules_lookup?: OnMatchRulesLookup;
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

export interface GTGraph {
	nodes: Map<NodeId, GTNode>;
	edges: Map<EdgeIdString, GTEdge>;
	addNode(
		data: GTNodeDataType,
		token?: Token | null,
		label?: NodeLabel | null,
		type?: GTNodeType,
	): NodeId;
	addEdge(source: NodeId, target: NodeId, data: GTEdgeDataType): void;
	getNode(id: NodeId): GTNode | undefined;
	getEdge(source: NodeId, target: NodeId): GTEdge | undefined;
	childrenOfType?(nodeId: NodeId, type: GTNodeType): NodeId[];
	updateEdgeData?(source: NodeId, target: NodeId, data: GTEdgeDataType): void;
}

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

// =============================================================================
// RAW & CONSTRAINT RULE SCHEMAS
// =============================================================================

export interface RawRuleDict {
	production?: Production;
	tokens?: Tokens;
	cost?: Cost;
	prev_classes?: TokenClasses;
	prev_tokens?: Tokens;
	next_tokens?: Tokens;
	next_classes?: TokenClasses;
}

export interface RawOnMatchDict {
	prev_classes: TokenClasses;
	next_classes: TokenClasses;
	production: Production;
}

export interface RawWhitespaceDict {
	default: Token;
	token_class: TokenClass;
	consolidate: boolean;
}

export interface ConstraintDict {
	prev_classes?: TokenClasses;
	prev_tokens?: Tokens;
	next_tokens?: Tokens;
	next_classes?: TokenClasses;
}

// =============================================================================
// GRAPH NODE & EDGE STRUCTURES
// =============================================================================

export interface EngineNodeData {
	ordered_children?: Record<string, NodeId[]>;
	token_children?: Record<Token, NodeId>;
	rule_children?: NodeId[];
	rule_key?: RuleId;
	accepting?: boolean;
	[key: string]: unknown;
}

export interface EngineEdgeData {
	cost?: Cost;
	token?: Token;
	constraints?: ConstraintDict;
	[key: string]: unknown;
}

export type EngineGraphNode = Node<string, EngineNodeData>;
export type EngineGraphEdge = Edge<EngineEdgeData>;

// =============================================================================
// EASY READING & PROCESSOR INTERFACES
// =============================================================================

/**
 * Parsed output shape generated by processing raw Easy Reading input.
 * Matches Python's ProcessedSettingsDict TypedDict.
 */
export interface ProcessedSettingsDict {
	tokens: Record<Token, TokenClasses>;
	rules: RawRuleDict[];
	onmatch_rules: RawOnMatchDict[];
	whitespace: RawWhitespaceDict;
	metadata: Record<string, string | number | boolean>;
}

/**
 * Flexible input shape for raw Easy Reading configuration settings before processing.
 * Matches Python's EasyReadingInput type alias.
 */
export type EasyReadingInput = {
	tokens?: Record<string, string[]>;
	rules?: Record<string, string>;
	onmatch_rules?: Record<string, string>[];
	whitespace?: RawWhitespaceDict;
	metadata?: Record<string, string | number | boolean>;
	[key: string]: unknown;
};
