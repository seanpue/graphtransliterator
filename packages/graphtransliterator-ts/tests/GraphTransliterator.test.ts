// test/GraphTransliterator.test.ts

import { describe, expect, it } from "vitest";
import { DirectedGraph, VisitLoggingDirectedGraph } from "../src/Graphs.js";
import {
	allMatchesAt,
	fromEasyReadingSettings,
	fromEasyReadingYaml,
	graphTransliterator,
	matchRulesAt,
	tokenize,
	transliterate,
	transliterateReporting,
} from "../src/GraphTransliterator.js";
import {
	costOf,
	numTokensOf,
	tokenizerPatternFrom,
	tokensByClassOf,
	transliterationRuleOf,
} from "../src/initialize.js";
import type { EasyReadingSettings, TransliterationRule } from "../src/types.js";

// =============================================================================
// TEST MOCKS & FIXTURES
// =============================================================================

const mockSettings: EasyReadingSettings = {
	tokens: {
		a: ["class_a"],
		b: ["class_b"],
		c: ["class_c"],
		" ": ["wb"],
	},
	rules: {
		a: "A",
		b: "B",
		c: "C",
		"c c": "C*2",
		"( b b ) a": "a_after_bb",
		"a <class_c>": "a_before_class_c",
	},
	whitespace: {
		consolidate: true,
		default: " ",
		tokenClass: "wb",
	},
};

const sampleSettings: EasyReadingSettings = {
	tokens: {
		a: ["vowel"],
		b: ["consonant"],
		c: ["consonant"],
		sh: ["consonant"],
		" ": ["whitespace"],
	},
	rules: {
		a: "A",
		b: "B",
		sh: "SH",
		"c (a)": "K", // c before 'a' becomes K
	},
	whitespace: {
		consolidate: true,
		default: " ",
		tokenClass: "whitespace",
	},
};

const sampleYaml = `
tokens:
  a: ["vowel"]
  b: ["consonant"]
  sh: ["consonant"]
  " ": ["whitespace"]

rules:
  a: "A"
  b: "B"
  sh: "SH"

whitespace:
  consolidate: true
  default: " "
  token_class: "whitespace"
`;

// =============================================================================
// SUITE 1: CORE FRAMEWORK & INITIALIZATION
// =============================================================================

describe("GraphTransliterator Core Framework", () => {
	const config = fromEasyReadingSettings(mockSettings);
	const gt = graphTransliterator(config);

	describe("Initialization Utilities (initialize.ts)", () => {
		it("should correctly count tokens and constraints via numTokensOf", () => {
			const simpleRule: TransliterationRule = {
				tokens: ["a", "b"],
				production: "AB",
			};
			expect(numTokensOf(simpleRule)).toBe(2);

			const constrainedRule: TransliterationRule = {
				tokens: ["a"],
				prev_classes: ["class_b"],
				next_tokens: ["c"],
				production: "A_CONSTRAINED",
			};
			// 1 match token + 1 prev_class + 1 next_token = 3 total tokens/constraints
			expect(numTokensOf(constrainedRule)).toBe(3);
		});

		it("should calculate rule cost using costOf inverse formula", () => {
			const rule1Token: TransliterationRule = {
				tokens: ["a"],
				production: "A",
			};
			expect(costOf(rule1Token)).toBeCloseTo(Math.log2(1.5), 5);

			const rule3Tokens: TransliterationRule = {
				tokens: ["a"],
				prev_classes: ["class_b"],
				next_tokens: ["c"],
				production: "X",
			};
			expect(costOf(rule3Tokens)).toBeLessThan(costOf(rule1Token));
		});

		it("should automatically assign computed cost in transliterationRuleOf", () => {
			const rawRule = { tokens: ["x"], production: "X" };
			const rule = transliterationRuleOf(rawRule);

			expect(rule.cost).toBeDefined();
			expect(rule.cost).toBe(costOf(rawRule));
		});

		it("should preserve explicitly defined costs in transliterationRuleOf", () => {
			const rawRule = { tokens: ["x"], production: "X", cost: 0.123 };
			const rule = transliterationRuleOf(rawRule);

			expect(rule.cost).toBe(0.123);
		});

		it("should group tokens by class correctly via tokensByClassOf", () => {
			const tokenMap = {
				a: ["vowel", "letter"],
				b: ["consonant", "letter"],
			};
			const classMap = tokensByClassOf(tokenMap);

			expect(classMap.get("vowel")).toEqual(new Set(["a"]));
			expect(classMap.get("consonant")).toEqual(new Set(["b"]));
			expect(classMap.get("letter")).toEqual(new Set(["a", "b"]));
		});

		it("should build regex pattern sorted by longest token first via tokenizerPatternFrom", () => {
			const pattern = tokenizerPatternFrom(["a", "aa", "b"]);
			expect(pattern).toBe("(aa|a|b)");
		});
	});

	describe("Core Operations & Context Matching", () => {
		it("should cleanly tokenize input, retaining explicit whitespace tokens", () => {
			const tokens = tokenize("a b", gt);
			expect(tokens).toEqual([" ", "a", " ", "b", " "]);
		});

		it("should execute basic direct token transformations", () => {
			expect(transliterate("a", gt)).toBe("A");
			expect(transliterate("cc", gt)).toBe("C*2");
		});

		it("should successfully match rules conditioned on a preceding token context", () => {
			const result = transliterate("bba", gt);
			expect(result).toBe("BBa_after_bb");
		});

		it("should successfully match rules conditioned on a class lookahead", () => {
			const result = transliterate("ac", gt);
			expect(result).toBe("a_before_class_cC");
		});

		it("should collect concurrent valid choices via allMatchesAt", () => {
			const stream = tokenize("aa", gt);
			const ruleIds = allMatchesAt(1, stream, gt);

			expect(ruleIds.length).toBeGreaterThanOrEqual(1);
			expect(typeof ruleIds[0]).toBe("number");
		});

		it("should generate detailed transliteration reports via transliterateReporting", () => {
			const report = transliterateReporting("a", gt);
			expect(report).toHaveLength(1);
			expect(report[0]).toMatchObject({
				type: "RuleProduction",
				tokenIdx: 1,
				tokens: ["a"],
				production: "A",
			});
		});
	});

	describe("Rule Pruning via prunedOf", () => {
		it("should return a new instance and leave the original instance unmutated", () => {
			const prunedGt = gt.prunedOf("C*2");

			expect(prunedGt).not.toBe(gt);
			expect(transliterate("cc", gt)).toBe("C*2");
			expect(transliterate("cc", prunedGt)).toBe("CC");
		});

		it("should accept a single string production and filter it out completely", () => {
			const prunedGt = gt.prunedOf("a_before_class_c");

			expect(transliterate("ac", prunedGt)).toBe("AC");
		});

		it("should accept an array of strings and drop multiple matching rules simultaneously", () => {
			const prunedGt = gt.prunedOf(["C*2", "a_after_bb"]);

			expect(transliterate("cc", prunedGt)).toBe("CC");
			expect(transliterate("bba", prunedGt)).toBe("BBA");
		});

		it("should handle pruning non-existent productions gracefully without altering behavior", () => {
			const prunedGt = gt.prunedOf("NON_EXISTENT_PRODUCTION");

			expect(transliterate("cc", prunedGt)).toBe("C*2");
			expect(transliterate("ac", prunedGt)).toBe("a_before_class_cC");
		});
	});

	describe("DirectedGraph Methods & Inspection", () => {
		it("should inspect graph nodes and edges on the compiled GT instance", () => {
			const graph = gt.graph;
			expect(graph.nodes.length).toBeGreaterThan(0);

			const startNode = graph.getNode(0);
			expect(startNode).not.toBeNull();
		});

		it("should correctly add nodes and edges using DirectedGraph instance methods", () => {
			const graph = new DirectedGraph();

			const idA = graph.addNode({ value: 1 }, "a", "LabelA", "TokenNode");
			const idB = graph.addNode({ value: 2 }, "b", "LabelB", "TokenNode");

			expect(idA).toBe(0);
			expect(idB).toBe(1);

			graph.addEdge(idA, idB, { cost: 5.0 });
			expect(graph.edges.length).toBe(1);

			const edge = graph.getEdge(idA, idB);
			expect(edge).toEqual({ cost: 5.0 });
		});

		it("should accurately log traversal and check coverage in VisitLoggingDirectedGraph", () => {
			const baseGraph = new DirectedGraph();
			const idA = baseGraph.addNode(null, "a");
			const idB = baseGraph.addNode(null, "b");
			baseGraph.addEdge(idA, idB);

			const loggingGraph = new VisitLoggingDirectedGraph(baseGraph);

			expect(() => loggingGraph.checkCoverage(true)).toThrowError(
				"Incomplete graph edge coverage: 0->1",
			);

			loggingGraph.visitNode(idA);
			loggingGraph.visitNode(idB);
			loggingGraph.visitEdge(idA, idB);

			expect(loggingGraph.checkCoverage(true)).toBe(true);
		});
	});
});

// =============================================================================
// SUITE 2: INSTANCE METHOD vs STANDALONE FUNCTION PARITY
// =============================================================================

describe("GraphTransliterator Class Methods & Standalone Parity", () => {
	describe("Tokenization", () => {
		it("tokenizes correctly via instance method", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);

			const tokens = gt.tokenize("a b sh");
			expect(tokens).toEqual([" ", "a", " ", "b", " ", "sh", " "]);
		});

		it("tokenizes correctly via standalone function", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);

			const tokens = tokenize("a b sh", gt);
			expect(tokens).toEqual([" ", "a", " ", "b", " ", "sh", " "]);
		});
	});

	describe("Transliteration", () => {
		it("transliterates via instance method vs standalone function", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);
			const input = "sh a b c a";

			const resultFromMethod = gt.transliterate(input);
			const resultFromFunction = transliterate(input, gt);

			expect(resultFromMethod).toBe("SHABA");
			expect(resultFromMethod).toBe(resultFromFunction);
		});

		it("prunes rules using prunedOf and tests instance transliteration", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);

			const prunedGt = gt.prunedOf("SH");

			expect(gt.transliterate("sh a")).toBe("SHA");
			expect(prunedGt.transliterate("sh a")).toBe("A");
		});
	});

	describe("Reporting", () => {
		it("returns transliteration report via instance method", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);

			const report = gt.transliterateReporting("sh a");

			expect(report).toHaveLength(2);
			expect(report[0]).toMatchObject({
				type: "RuleProduction",
				tokens: ["sh"],
				production: "SH",
			});
			expect(report[1]).toMatchObject({
				type: "RuleProduction",
				tokens: ["a"],
				production: "A",
			});
		});

		it("standalone transliterateReporting matches instance method output", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);

			const instanceReport = gt.transliterateReporting("a b");
			const standaloneReport = transliterateReporting("a b", gt);

			expect(instanceReport).toEqual(standaloneReport);
		});
	});

	describe("Match Finding", () => {
		it("finds matching rules at index using matchRulesAt", () => {
			const config = fromEasyReadingSettings(sampleSettings);
			const gt = graphTransliterator(config);
			const tokens = gt.tokenize("a b");

			const matchesFromMethod = gt.matchRulesAt(1, tokens);
			const matchesFromFunc = matchRulesAt(1, tokens, gt);

			expect(matchesFromMethod.length).toBeGreaterThan(0);
			expect(matchesFromMethod).toEqual(matchesFromFunc);
		});
	});

	describe("YAML Construction", () => {
		it("instantiates and transliterates directly from YAML string", () => {
			const gt = fromEasyReadingYaml(sampleYaml);
			const output = gt.transliterate("a sh b");

			expect(output).toBe("ASHB");
		});

		it("throws error when invalid YAML is passed", () => {
			expect(() => fromEasyReadingYaml("")).toThrow("YAML string is empty");
			expect(() => fromEasyReadingYaml("foo: bar")).toThrow(
				"missing required EasyReadingSettings fields",
			);
		});
	});
});
