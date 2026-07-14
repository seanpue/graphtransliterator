[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / updateEdgeData

# Function: updateEdgeData()

> **updateEdgeData**\<`T`, `N`, `E`\>(`graph`, `head`, `tail`, `newData`): [`DirectedGraph`](../interfaces/DirectedGraph.md)\<`T`, `N`, `E`\>

Defined in: [Graphs.ts:314](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L314)

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
