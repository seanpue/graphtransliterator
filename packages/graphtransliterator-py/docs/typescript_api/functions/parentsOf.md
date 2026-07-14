[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / parentsOf

# Function: parentsOf()

> **parentsOf**\<`T`, `N`, `E`\>(`graph`, `childId`): `number`[]

Defined in: [Graphs.ts:189](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L189)

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
