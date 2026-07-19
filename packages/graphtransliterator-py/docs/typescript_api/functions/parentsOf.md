[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / parentsOf

# Function: parentsOf()

> **parentsOf**\<`T`, `N`, `E`\>(`graph`, `childId`): `number`[]

Defined in: [Graphs.ts:188](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L188)

Returns an ordered array of parent node identifiers feeding into a child target node.
Achieves high performance by leveraging the pre-compiled O(1) predecessors lookup index.

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

### childId

`number`

## Returns

`number`[]
