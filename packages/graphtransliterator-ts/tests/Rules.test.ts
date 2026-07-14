import { describe, it, expect } from "vitest";
import { costOf } from "../src/Rules";

describe("Rules Utility Framework", () => {
    it("should calculate a baseline cost for a rule with zero optional constraints", () => {
        // A rule with just 1 token match condition
        const baselineCost = costOf(null, null, ["a"], null, null);

        // n = 1, so cost = 1 / (1 + 1) = 0.5
        expect(baselineCost).toBe(0.5);
    });

    it("should calculate lower costs for rules with more specific constraints", () => {
        // Rule A: Generic match on token 'b' (n = 1) -> Cost = 0.5
        const genericCost = costOf(null, null, ["b"], null, null);

        // Rule B: Match on token 'b', but requires a previous 'consonant' class and a next token 'c'
        // n = 1 (prev class) + 1 (token) + 1 (next token) = 3 -> Cost = 1 / (1 + 3) = 0.25
        const specificCost = costOf(["consonant"], null, ["b"], ["c"], null);

        // Specific rules must have a lower cost so they sort to the top of the stack[cite: 2]
        expect(specificCost).toBeLessThan(genericCost);
        expect(specificCost).toBe(0.25);
    });

    it("should handle undefined or empty arrays identically to null values", () => {
        const costWithNull = costOf(null, null, ["xyz"], null, null);
        const costWithUndefined = costOf(
            undefined,
            undefined,
            ["xyz"],
            undefined,
            undefined,
        );
        const costWithEmptyArrays = costOf([], [], ["xyz"], [], []);

        expect(costWithNull).toBe(0.5);
        expect(costWithUndefined).toBe(0.5);
        expect(costWithEmptyArrays).toBe(0.5);
    });
});
