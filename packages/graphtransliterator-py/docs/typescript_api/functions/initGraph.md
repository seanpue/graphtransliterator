[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / initGraph

# Function: initGraph()

> **initGraph**\<`T`, `N`, `E`\>(`nodes?`, `edges?`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:99](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L99)

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
