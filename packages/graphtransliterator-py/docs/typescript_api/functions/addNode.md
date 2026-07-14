[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / addNode

# Function: addNode()

> **addNode**\<`T`, `N`, `E`\>(`graph`, `type_`, `label`, `data`): \[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Node`](../interfaces/Node.md)\<`T`, `N`\>\]

Defined in: [Graphs.ts:220](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L220)

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
