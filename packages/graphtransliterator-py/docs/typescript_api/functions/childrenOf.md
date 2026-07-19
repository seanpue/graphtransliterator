[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / childrenOf

# Function: childrenOf()

> **childrenOf**\<`T`, `N`, `E`\>(`graph`, `parentId`): `number`[]

Defined in: [Graphs.ts:174](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L174)

Returns an ordered array of children node identifiers connected directly from a parent node.
Achieves high performance by leveraging the pre-compiled O(1) successors lookup index.

Ordering: Sorted ascending by numeric NodeId values.

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

## Returns

`number`[]
