[**graphtransliterator**](../README.md)

***

[graphtransliterator](../README.md) / Node

# Interface: Node\<T, N\>

Defined in: [Graphs.ts:32](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L32)

A strongly typed vertex node within the directed graph layout.

## Type Parameters

### T

`T`

User-defined categorical discriminant flag (e.g., node layout variant variants).

### N

`N`

Payload state type tailored to the node's specific variant data schema.

## Properties

### data

> **data**: `N`

Defined in: [Graphs.ts:40](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L40)

Arbitrary operational metadata carried by this specific vertex.

***

### id

> **id**: `number`

Defined in: [Graphs.ts:34](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L34)

Array index or numeric placement identifier unique to this node.

***

### label

> **label**: `string`

Defined in: [Graphs.ts:38](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L38)

Traceable structural descriptor or naming label.

***

### type\_

> **type\_**: `T`

Defined in: [Graphs.ts:36](https://github.com/seanpue/graphtransliterator/blob/67b1064e1d86c3350ed11de54d845d3e9cf61897/packages/graphtransliterator-ts/src/Graphs.ts#L36)

Categorical variant classification tag used for domain filtering.
