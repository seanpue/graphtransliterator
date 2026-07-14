[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / costOf

# Function: costOf()

> **costOf**(`prevClasses`, `prevTokens`, `tokens`, `nextTokens`, `nextClasses`): `number`

Defined in: [Rules.ts:104](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Rules.ts#L104)

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
