import { describe, it, expect } from "vitest";
import {
    fromEasyReadingSettings,
    graphTransliterator,
    transliterate,
    tokenize,
    allMatchesAt,
} from "../src/GraphTransliterator.js";
import type { EasyReadingSettings } from "../src/GraphTransliterator.js";

describe("GraphTransliterator Core Framework", () => {
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
            // Spaces around parentheses ensure they are parsed as constraints
            "( b b ) a": "a_after_bb",
            "a <class_c>": "a_before_class_c",
        },
        whitespace: {
            consolidate: true,
            defaultToken: " ",
            tokenClass: "wb",
        },
    };

    const config = fromEasyReadingSettings(mockSettings);
    const gt = graphTransliterator(config);

    it("should cleanly tokenize input, retaining explicit whitespace tokens", () => {
        const tokens = tokenize("a b", gt);
        expect(tokens).toEqual([" ", "a", " ", "b", " "]);
    });

    it("should execute basic direct token transformations", () => {
        expect(transliterate("a", gt)).toBe("A");
        expect(transliterate("cc", gt)).toBe("C*2");
    });

    it("should successfully match rules conditioned on a preceding token context", () => {
        // 'b' -> 'B', 'b' -> 'B', and 'a' (with 'b b' lookbehind) -> 'a_after_bb'
        const result = transliterate("bba", gt);
        expect(result).toBe("BBa_after_bb");
    });

    it("should successfully match rules conditioned on a class lookahead", () => {
        // 'a' (with class_c lookahead) -> 'a_before_class_c', 'c' -> 'C'
        const result = transliterate("ac", gt);
        expect(result).toBe("a_before_class_cC");
    });

    it("should collect concurrent valid choices via allMatchesAt", () => {
        const stream = tokenize("aa", gt);
        const ruleIds = allMatchesAt(1, stream, gt);

        expect(ruleIds.length).toBeGreaterThanOrEqual(1);
        expect(typeof ruleIds[0]).toBe("number");
    });
});
