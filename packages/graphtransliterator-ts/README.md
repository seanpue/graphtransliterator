# Graph Transliterator (TypeScript)

A TypeScript/JavaScript implementation of **Graph Transliterator**—a tool that converts text between scripts, transliteration schemes, or character encodings using custom graph-based rules.

[![npm version](https://img.shields.io/npm/v/graphtransliterator.svg)](https://www.npmjs.com/package/graphtransliterator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/graphtransliterator/badge/?version=latest)](https://graphtransliterator.readthedocs.io/)

---

## ✨ Features

- **Context-Aware Transliteration:** Define rules based on preceding or following tokens and token classes.
- **Contextual "On Match" Rules:** Insert production tokens when specific token classes adjoin.
- **Whitespace Management:** Configure default whitespace tokens and automatic whitespace consolidation.
- **Automatic Cost Ordering:** Rules automatically order based on match length (longest match preferred).
- **Ambiguity Checking:** Detects overlapping rules of equal cost during graph initialization.
- **Directed Graph Engine:** Builds an internal directed tree and runs a best-first search.
- **First-Class TypeScript Support:** Full type safety out of the box with bundled declaration files.

---

## 📦 Installation

Install using `pnpm`, `npm`, or `yarn`:

```bash
# pnpm
pnpm add graphtransliterator

# npm
npm install graphtransliterator

# yarn
yarn add graphtransliterator
```

---

## 💡 Quick Example

```typescript
import { GraphTransliterator } from "graphtransliterator";

const gt = new GraphTransliterator({
  tokens: {
    "h": ["consonant"],
    "i": ["vowel"],
    " ": ["whitespace"]
  },
  rules: [
    { rule: ["h"], production: "\u2149" }, // ᴉ (LATIN SMALL LETTER TURNED I)
    { rule: ["i"], production: "\u2148" }, // ɥ (LATIN SMALL LETTER TURNED H)
    { rule: ["i"], production: "\u2148!", prev_classes: ["whitespace", "h"] }
  ],
  onmatch_rules: [
    { prev_class: "whitespace", next_class: "consonant", production: "¡" }
  ],
  whitespace: {
    default: " ",
    consolidate: true,
    token_class: "whitespace"
  },
  metadata: {
    title: "Upside Down Greeting Transliterator",
    version: "1.0.0"
  }
});

console.log(gt.transliterate("hi")); // Output: '¡ᴉɥ!'
```

---

## 📚 Documentation & Repository

For complete details on API references, schema options, rule ordering, bundled transliterators, and Python equivalents, check out our full documentation:

- **TypeScript API Docs:** [Read The Docs — TypeScript Guide](https://graphtransliterator.readthedocs.io/en/latest/typescript.html)
- **Full Documentation:** [Read The Docs Homepage](https://graphtransliterator.readthedocs.io/)
- **Repository:** [GitHub Repository](https://github.com/seanpue/graphtransliterator)

---

## 📄 License

[MIT](LICENSE) © 2026 University of Maryland
