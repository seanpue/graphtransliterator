[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / updateNode

# Function: updateNode()

> **updateNode**\<`T`, `N`, `E`\>(`graph`, `targetNodeId`, `updater`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:287](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L287)

In-place modification function overriding data properties tied to a specific node coordinate.
If the provided `targetNodeId` falls out of the collection boundary bounds, the original topology is returned unmodified.

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

### targetNodeId

`number`

### updater

(`oldData`) => `N`

## Returns

[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>
