[**graphtransliterator-ts**](../README.md)

***

[graphtransliterator-ts](../README.md) / DirectedGraph

# Interface: DirectedGraph\<T, N, E\>

Defined in: [Graphs.ts:85](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L85)

Monolithic directed graph topology with integrated neighborhood lookup acceleration indexes.

## Type Parameters

### T

`T`

Structural node classification type.

### N

`N`

Vertex payload definition.

### E

`E`

Edge transition cost payload definition.

## Properties

### edges

> **edges**: `Map`\<`string`, [`Edge`](Edge.md)\<`E`\>\>

Defined in: [Graphs.ts:89](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L89)

Hash lookup container connecting edge ID string coordinates directly to transition payloads.

***

### nodes

> **nodes**: [`Node`](Node.md)\<`T`, `N`\>[]

Defined in: [Graphs.ts:87](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L87)

Array collection keeping track of all registered nodes mapped directly to their ID positions.

***

### predecessors

> **predecessors**: `Map`\<`number`, `Set`\<`number`\>\>

Defined in: [Graphs.ts:93](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L93)

Inverted index mapping a child NodeId back to its set of parent source NodeIds for O(1) lookbehinds.

***

### successors

> **successors**: `Map`\<`number`, `Set`\<`number`\>\>

Defined in: [Graphs.ts:91](https://github.com/seanpue/graphtransliterator/blob/83f4eb8e6b7957664bb77a2ded02cf6a46ce9fff/packages/graphtransliterator-ts/src/Graphs.ts#L91)

Inverted index mapping a parent NodeId directly to its set of child target NodeIds for O(1) traversal.
