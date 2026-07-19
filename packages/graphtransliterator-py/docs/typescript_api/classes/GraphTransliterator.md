[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / GraphTransliterator

# Class: GraphTransliterator

Defined in: [GraphTransliterator.ts:122](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L122)

## Constructors

### Constructor

> **new GraphTransliterator**(`config`): `GraphTransliterator`

Defined in: [GraphTransliterator.ts:134](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L134)

#### Parameters

##### config

###### graph

[`GTGraph`](../type-aliases/GTGraph.md)

###### metadata?

[`Metadata`](../type-aliases/Metadata.md)

###### onMatchRules?

[`OnMatchRules`](../type-aliases/OnMatchRules.md)

###### onMatchRulesLookup?

`Map`

###### rules

[`TransliterationRules`](../type-aliases/TransliterationRules.md)

###### tokenizerPattern

`RegExp`

###### tokenizerPatternStr

`string`

###### tokens

`Record`\<[`Token`](../type-aliases/Token.md), [`TokenClasses`](../type-aliases/TokenClasses.md)\>

###### tokensByClass

`Map`

###### whiteSpace

[`WhitespaceRule`](../interfaces/WhitespaceRule.md)

#### Returns

`GraphTransliterator`

## Properties

### graph

> **graph**: [`GTGraph`](../type-aliases/GTGraph.md)

Defined in: [GraphTransliterator.ts:132](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L132)

***

### metadata?

> `optional` **metadata?**: [`Metadata`](../type-aliases/Metadata.md)

Defined in: [GraphTransliterator.ts:127](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L127)

***

### onMatchRules?

> `optional` **onMatchRules?**: [`OnMatchRules`](../type-aliases/OnMatchRules.md)

Defined in: [GraphTransliterator.ts:126](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L126)

***

### onMatchRulesLookup?

> `optional` **onMatchRulesLookup?**: `Map`

Defined in: [GraphTransliterator.ts:128](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L128)

***

### rules

> **rules**: [`TransliterationRules`](../type-aliases/TransliterationRules.md)

Defined in: [GraphTransliterator.ts:124](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L124)

***

### tokenizerPattern

> **tokenizerPattern**: `RegExp`

Defined in: [GraphTransliterator.ts:130](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L130)

***

### tokenizerPatternStr

> **tokenizerPatternStr**: `string`

Defined in: [GraphTransliterator.ts:131](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L131)

***

### tokens

> **tokens**: `Record`\<[`Token`](../type-aliases/Token.md), [`TokenClasses`](../type-aliases/TokenClasses.md)\>

Defined in: [GraphTransliterator.ts:123](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L123)

***

### tokensByClass

> **tokensByClass**: `Map`

Defined in: [GraphTransliterator.ts:129](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L129)

***

### whiteSpace

> **whiteSpace**: [`WhitespaceRule`](../interfaces/WhitespaceRule.md)

Defined in: [GraphTransliterator.ts:125](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L125)

## Methods

### prunedOf()

> **prunedOf**(`productions`): `GraphTransliterator`

Defined in: [GraphTransliterator.ts:162](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L162)

Returns a new GraphTransliterator instance with rules filtered out
based on their production outputs.

#### Parameters

##### productions

`string` \| `string`[]

#### Returns

`GraphTransliterator`
