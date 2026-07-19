[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / updateEdgeData

# Function: updateEdgeData()

> **updateEdgeData**\<`T`, `N`, `E`\>(`graph`, `head`, `tail`, `newData`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:313](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L313)

In-place modification utility targeting structural weight attributes carried by directional edge keys.
If the specified pathway connection coordinates do not exist, the context configuration payload is returned untouched.

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

### newData

`E`

## Returns

[`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>
