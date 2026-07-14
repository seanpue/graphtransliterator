[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / childrenOf

# Function: childrenOf()

> **childrenOf**\<`T`, `N`, `E`\>(`graph`, `parentId`): `number`[]

Defined in: [Graphs.ts:175](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L175)

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
