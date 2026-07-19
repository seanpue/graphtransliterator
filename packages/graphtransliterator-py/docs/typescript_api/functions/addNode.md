[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / addNode

# Function: addNode()

> **addNode**\<`T`, `N`, `E`\>(`graph`, `type_`, `label`, `data`): \[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Node`](../interfaces/Node.md)\<`T`, `N`\>\]

Defined in: [Graphs.ts:219](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L219)

Stitches a fresh vertex node onto an existing graph context using pure state propagation.

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

### type\_

`T`

### label

`string`

### data

`N`

## Returns

\[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Node`](../interfaces/Node.md)\<`T`, `N`\>\]

A tuple containing the updated `DirectedGraph` instance alongside the newly minted `Node` payload.
