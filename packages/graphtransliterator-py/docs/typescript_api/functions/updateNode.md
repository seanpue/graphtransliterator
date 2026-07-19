[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / updateNode

# Function: updateNode()

> **updateNode**\<`T`, `N`, `E`\>(`graph`, `targetNodeId`, `updater`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:286](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L286)

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
