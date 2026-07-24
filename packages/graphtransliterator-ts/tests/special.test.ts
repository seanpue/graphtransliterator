import { describe, expect, it } from "vitest";
import type { EasyReadingSettings } from "../src/GraphTransliterator.js";
import {
    allMatchesAt,
    fromEasyReadingSettings,
    graphTransliterator,
    tokenize,
    transliterate,
} from "../src/GraphTransliterator.js";
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
            default: " ",
            tokenClass: "wb",
        },
    };

    const config = fromEasyReadingSettings(mockSettings);
    const gt = graphTransliterator(config);
    it("should cleanly tokenize input, retaining explicit whitespace tokens", () => {
        const tokens = tokenize("a b", gt);
        console.log(tokens);
        expect(tokens).toEqual([" ", "a", " ", "b", " "]);
    });
});
