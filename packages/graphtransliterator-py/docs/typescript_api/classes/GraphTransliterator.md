[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / GraphTransliterator

# Class: GraphTransliterator

Defined in: [GraphTransliterator.ts:124](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L124)

## Constructors

### Constructor

> **new GraphTransliterator**(`config`): `GraphTransliterator`

Defined in: [GraphTransliterator.ts:136](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L136)

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

Defined in: [GraphTransliterator.ts:134](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L134)

***

### metadata?

> `optional` **metadata?**: [`Metadata`](../type-aliases/Metadata.md)

Defined in: [GraphTransliterator.ts:129](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L129)

***

### onMatchRules?

> `optional` **onMatchRules?**: [`OnMatchRules`](../type-aliases/OnMatchRules.md)

Defined in: [GraphTransliterator.ts:128](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L128)

***

### onMatchRulesLookup?

> `optional` **onMatchRulesLookup?**: `Map`

Defined in: [GraphTransliterator.ts:130](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L130)

***

### rules

> **rules**: [`TransliterationRules`](../type-aliases/TransliterationRules.md)

Defined in: [GraphTransliterator.ts:126](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L126)

***

### tokenizerPattern

> **tokenizerPattern**: `RegExp`

Defined in: [GraphTransliterator.ts:132](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L132)

***

### tokenizerPatternStr

> **tokenizerPatternStr**: `string`

Defined in: [GraphTransliterator.ts:133](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L133)

***

### tokens

> **tokens**: `Record`\<[`Token`](../type-aliases/Token.md), [`TokenClasses`](../type-aliases/TokenClasses.md)\>

Defined in: [GraphTransliterator.ts:125](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L125)

***

### tokensByClass

> **tokensByClass**: `Map`

Defined in: [GraphTransliterator.ts:131](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L131)

***

### whiteSpace

> **whiteSpace**: [`WhitespaceRule`](../interfaces/WhitespaceRule.md)

Defined in: [GraphTransliterator.ts:127](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L127)

## Methods

### prunedOf()

> **prunedOf**(`productions`): `GraphTransliterator`

Defined in: [GraphTransliterator.ts:164](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/GraphTransliterator.ts#L164)

Returns a new GraphTransliterator instance with rules filtered out
based on their production outputs.

#### Parameters

##### productions

`string` \| `string`[]

#### Returns

`GraphTransliterator`
