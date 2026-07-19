[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / Edge

# Interface: Edge\<E\>

Defined in: [Graphs.ts:52](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L52)

A directed edge connecting a source node to a target destination node.

## Type Parameters

### E

`E`

The numeric weight or contextual operational cost structure of the transition.

## Properties

### data

> **data**: `E`

Defined in: [Graphs.ts:58](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L58)

Arbitrary payload metrics or step execution costs assigned to this connection.

***

### head

> **head**: `number`

Defined in: [Graphs.ts:54](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L54)

The tail vertex identifier where the directional path begins (Source Node).

***

### tail

> **tail**: `number`

Defined in: [Graphs.ts:56](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L56)

The head vertex identifier where the directional path terminates (Target Node).
