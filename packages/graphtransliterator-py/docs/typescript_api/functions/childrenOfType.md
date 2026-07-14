[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / childrenOfType

# Function: childrenOfType()

> **childrenOfType**\<`T`, `N`, `E`\>(`graph`, `parentId`, `nodeType`): `number`[]

Defined in: [Graphs.ts:201](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L201)

Filters the downstream child array elements from a parent, selecting entries
that match an explicit structural type discriminant.

## Type Parameters

### T

`T`

### N

`N`

### E

`E`

## Parameters

### graph

[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

### parentId

`number`

### nodeType

`T`

## Returns

`number`[]
