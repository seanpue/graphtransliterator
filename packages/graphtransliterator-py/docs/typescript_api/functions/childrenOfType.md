[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / childrenOfType

# Function: childrenOfType()

> **childrenOfType**\<`T`, `N`, `E`\>(`graph`, `parentId`, `nodeType`): `number`[]

Defined in: [Graphs.ts:200](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L200)

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
