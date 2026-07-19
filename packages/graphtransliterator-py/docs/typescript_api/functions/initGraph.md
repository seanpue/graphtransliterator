[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / initGraph

# Function: initGraph()

> **initGraph**\<`T`, `N`, `E`\>(`nodes?`, `edges?`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:99](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L99)

Spins up an empty, immutable execution graph topology initialized with raw structural assets.

## Type Parameters

### T

`T`

### N

`N`

### E

`E`

## Parameters

### nodes?

[`Node`](../interfaces/Node.md)\<`T`, `N`\>[] = `[]`

### edges?

`Map`\<`string`, [`Edge`](../interfaces/Edge.md)\<`E`\>\> = `...`

## Returns

[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>
