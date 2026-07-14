// src/Graphs.ts
/**
 * @module Graphs
 * A high-performance, immutable directed graph framework optimized for state transition systems.
 *
 * @description
 * This module provides the topological infrastructure for building and traversing Directed Acyclic
 * Word Graphs (DAWGs) and Finite State Transducers (FSTs). It utilizes an adjacency index cache
 * to achieve O(1) node neighbor resolutions, eliminating runtime edge-table scanning bottlenecks
 * during lookups.
 */

// =============================================================================
// NODE DECLARATIONS
// =============================================================================

/**
 * Unique numeric identifier for an explicit vertex node.
 * Node identifiers are contiguous integers starting from zero.
 */
export type NodeId = number;

/** Human-readable symbolic label attached to a vertex for diagnostic tracing. */
export type NodeLabel = string;

/**
 * A strongly typed vertex node within the directed graph layout.
 *
 * @template T - User-defined categorical discriminant flag (e.g., node layout variant variants).
 * @template N - Payload state type tailored to the node's specific variant data schema.
 */
export interface Node<T, N> {
    /** Array index or numeric placement identifier unique to this node. */
    id: NodeId;
    /** Categorical variant classification tag used for domain filtering. */
    type_: T;
    /** Traceable structural descriptor or naming label. */
    label: NodeLabel;
    /** Arbitrary operational metadata carried by this specific vertex. */
    data: N;
}

// =============================================================================
// EDGE DECLARATIONS
// =============================================================================

/**
 * A directed edge connecting a source node to a target destination node.
 *
 * @template E - The numeric weight or contextual operational cost structure of the transition.
 */
export interface Edge<E> {
    /** The tail vertex identifier where the directional path begins (Source Node). */
    head: NodeId;
    /** The head vertex identifier where the directional path terminates (Target Node). */
    tail: NodeId;
    /** Arbitrary payload metrics or step execution costs assigned to this connection. */
    data: E;
}

/**
 * Serialized map key identifier string tracking matching edge boundaries.
 * Enforces the invariant: `${head},${tail}`.
 */
export type EdgeIdString = string;

/**
 * Generates the standardized Map key signature from a directional connection coordinate.
 */
function toEdgeId(head: NodeId, tail: NodeId): EdgeIdString {
    return `${head},${tail}`;
}

// =============================================================================
// DIRECTED GRAPH TOPOLOGY
// =============================================================================

/**
 * Monolithic directed graph topology with integrated neighborhood lookup acceleration indexes.
 *
 * @template T - Structural node classification type.
 * @template N - Vertex payload definition.
 * @template E - Edge transition cost payload definition.
 */
export interface DirectedGraph<T, N, E> {
    /** Array collection keeping track of all registered nodes mapped directly to their ID positions. */
    nodes: Node<T, N>[];
    /** Hash lookup container connecting edge ID string coordinates directly to transition payloads. */
    edges: Map<EdgeIdString, Edge<E>>;
    /** Inverted index mapping a parent NodeId directly to its set of child target NodeIds for O(1) traversal. */
    successors: Map<NodeId, Set<NodeId>>;
    /** Inverted index mapping a child NodeId back to its set of parent source NodeIds for O(1) lookbehinds. */
    predecessors: Map<NodeId, Set<NodeId>>;
}

/**
 * Spins up an empty, immutable execution graph topology initialized with raw structural assets.
 */
export function initGraph<T, N, E>(
    nodes: Node<T, N>[] = [],
    edges: Map<EdgeIdString, Edge<E>> = new Map(),
): DirectedGraph<T, N, E> {
    const successors = new Map<NodeId, Set<NodeId>>();
    const predecessors = new Map<NodeId, Set<NodeId>>();

    // Initialize tracking buckets for any pre-loaded nodes
    for (const node of nodes) {
        successors.set(node.id, new Set());
        predecessors.set(node.id, new Set());
    }

    // Sync index arrays if pre-populated records are fed into initializer[cite: 5]
    for (const edge of edges.values()) {
        if (!successors.has(edge.head)) successors.set(edge.head, new Set());
        if (!predecessors.has(edge.tail))
            predecessors.set(edge.tail, new Set());
        successors.get(edge.head)!.add(edge.tail);
        predecessors.get(edge.tail)!.add(edge.head);
    }

    return { nodes, edges, successors, predecessors };
}

// =============================================================================
// HIGH-PERFORMANCE READ UTILITIES
// =============================================================================

/**
 * Grabs the precise node reference corresponding to an explicit identifier.
 */
export function getNode<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    id: NodeId,
): Node<T, N> | undefined {
    return graph.nodes[id];
}

/**
 * Validates the existence of a custom structural vertex point.
 */
export function hasNode<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    id: NodeId,
): boolean {
    return id >= 0 && id < graph.nodes.length;
}

/**
 * Direct evaluation query returning the explicit type variant assigned to a node coordinate.
 */
export function getNodeType<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    id: NodeId,
): T | undefined {
    return graph.nodes[id]?.type_;
}

/**
 * Resolves a directed edge connection interface bridging a head and tail transition point.
 */
export function getEdge<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    head: NodeId,
    tail: NodeId,
): Edge<E> | undefined {
    return graph.edges.get(toEdgeId(head, tail));
}

/**
 * Returns an ordered array of children node identifiers connected directly from a parent node.
 * Achieves high performance by leveraging the pre-compiled O(1) successors lookup index.
 *
 * Ordering: Sorted ascending by numeric NodeId values.
 */
export function childrenOf<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    parentId: NodeId,
): NodeId[] {
    const targets = graph.successors.get(parentId);
    return targets ? Array.from(targets).sort((a, b) => a - b) : [];
}

/**
 * Returns an ordered array of parent node identifiers feeding into a child target node.
 * Achieves high performance by leveraging the pre-compiled O(1) predecessors lookup index.
 *
 * Ordering: Sorted ascending by numeric NodeId values.
 */
export function parentsOf<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    childId: NodeId,
): NodeId[] {
    const sources = graph.predecessors.get(childId);
    return sources ? Array.from(sources).sort((a, b) => a - b) : [];
}

/**
 * Filters the downstream child array elements from a parent, selecting entries
 * that match an explicit structural type discriminant.
 */
export function childrenOfType<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    parentId: NodeId,
    nodeType: T,
): NodeId[] {
    return childrenOf(graph, parentId).filter(
        (nodeId) => getNodeType(graph, nodeId) === nodeType,
    );
}

// =============================================================================
// IMMUTABLE WRITE UTILITIES
// =============================================================================

/**
 * Stitches a fresh vertex node onto an existing graph context using pure state propagation.
 *
 * @returns A tuple containing the updated `DirectedGraph` instance alongside the newly minted `Node` payload.
 */
export function addNode<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    type_: T,
    label: NodeLabel,
    data: N,
): [DirectedGraph<T, N, E>, Node<T, N>] {
    const nextId = graph.nodes.length;
    const newNode: Node<T, N> = { id: nextId, type_, label, data };

    const nextNodes = [...graph.nodes, newNode];
    const nextSuccessors = new Map(graph.successors);
    const nextPredecessors = new Map(graph.predecessors);

    nextSuccessors.set(nextId, new Set());
    nextPredecessors.set(nextId, new Set());

    return [
        {
            nodes: nextNodes,
            edges: graph.edges,
            successors: nextSuccessors,
            predecessors: nextPredecessors,
        },
        newNode,
    ];
}

/**
 * Registers an active transition pathway bridging two nodes together.
 * Generates an optimized internal cache mapping to prevent linear execution search penalties.
 */
export function addEdge<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    head: NodeId,
    tail: NodeId,
    data: E,
): [DirectedGraph<T, N, E>, Edge<E>] {
    const key = toEdgeId(head, tail);
    const newEdge: Edge<E> = { head, tail, data };

    const nextEdges = new Map(graph.edges);
    nextEdges.set(key, newEdge);

    const nextSuccessors = new Map(graph.successors);
    const nextPredecessors = new Map(graph.predecessors);

    if (!nextSuccessors.has(head)) nextSuccessors.set(head, new Set());
    nextSuccessors.get(head)!.add(tail);

    if (!nextPredecessors.has(tail)) nextPredecessors.set(tail, new Set());
    nextPredecessors.get(tail)!.add(head);

    return [
        {
            nodes: graph.nodes,
            edges: nextEdges,
            successors: nextSuccessors,
            predecessors: nextPredecessors,
        },
        newEdge,
    ];
}

/**
 * In-place modification function overriding data properties tied to a specific node coordinate.
 * If the provided `targetNodeId` falls out of the collection boundary bounds, the original topology is returned unmodified.
 */
export function updateNode<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    targetNodeId: NodeId,
    updater: (oldData: N) => N,
): DirectedGraph<T, N, E> {
    if (!hasNode(graph, targetNodeId)) return graph;

    const nextNodes = [...graph.nodes];
    const oldNode = nextNodes[targetNodeId];

    nextNodes[targetNodeId] = {
        ...oldNode,
        data: updater(oldNode.data),
    };

    return {
        nodes: nextNodes,
        edges: graph.edges,
        successors: graph.successors,
        predecessors: graph.predecessors,
    };
}

/**
 * In-place modification utility targeting structural weight attributes carried by directional edge keys.
 * If the specified pathway connection coordinates do not exist, the context configuration payload is returned untouched.
 */
export function updateEdgeData<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    head: NodeId,
    tail: NodeId,
    newData: E,
): DirectedGraph<T, N, E> {
    const key = toEdgeId(head, tail);
    if (!graph.edges.has(key)) return graph;

    const nextEdges = new Map(graph.edges);
    nextEdges.set(key, { head, tail, data: newData });

    return {
        nodes: graph.nodes,
        edges: nextEdges,
        successors: graph.successors,
        predecessors: graph.predecessors,
    };
}
