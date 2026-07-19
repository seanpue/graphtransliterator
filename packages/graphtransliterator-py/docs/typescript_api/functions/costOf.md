[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / costOf

# Function: costOf()

> **costOf**(`prevClasses`, `prevTokens`, `tokens`, `nextTokens`, `nextClasses`): `number`

Defined in: [Rules.ts:103](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Rules.ts#L103)

Calculate cost of a rule.

Rules with more total constraints (prev/next classes/tokens + matched tokens)
have lower cost and should be tried first (i.e. sort ascending by cost).

## Parameters

### prevClasses

[`TokenClasses`](../type-aliases/TokenClasses.md)

### prevTokens

[`Tokens`](../type-aliases/Tokens.md)

### tokens

[`Tokens`](../type-aliases/Tokens.md)

### nextTokens

[`Tokens`](../type-aliases/Tokens.md)

### nextClasses

[`TokenClasses`](../type-aliases/TokenClasses.md)

## Returns

`number`
