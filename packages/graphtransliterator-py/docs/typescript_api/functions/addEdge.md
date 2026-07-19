[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / addEdge

# Function: addEdge()

> **addEdge**\<`T`, `N`, `E`\>(`graph`, `head`, `tail`, `data`): \[[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>, [`Edge`](../interfaces/Edge.md)\<`E`\>\]

Defined in: [Graphs.ts:250](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L250)

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
