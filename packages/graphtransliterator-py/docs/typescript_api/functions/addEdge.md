[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / addEdge

# Function: addEdge()

> **addEdge**\<`T`, `N`, `E`\>(`graph`, `head`, `tail`, `data`): \[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Edge`](../interfaces/Edge.md)\<`E`\>\]

Defined in: [Graphs.ts:251](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L251)

Registers an active transition pathway bridging two nodes together.
Generates an optimized internal cache mapping to prevent linear execution search penalties.

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

### head

`number`

### tail

`number`

### data

`E`

## Returns

\[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Edge`](../interfaces/Edge.md)\<`E`\>\]
