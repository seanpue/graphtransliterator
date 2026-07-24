// src/Graphs.ts
/**
 * @module Graphs
 * A high-performance directed graph framework optimized for state transition systems.
 *
 * @description
 * Provides the topological infrastructure for building and traversing Directed Acyclic
 * Word Graphs (DAWGs) and Finite State Transducers (FSTs). Utilizes an adjacency index cache
 * to achieve O(1) node neighbor resolutions.
 */

import {
    Edge,
    EdgeIdString,
    LoadedGraphDict,
    Node,
    NodeId,
    NodeLabel,
} from "./types.js";

// =============================================================================
// EDGE IDENTIFIER HELPER
// =============================================================================

/**
 * Generates the standardized Map key signature from a directional connection coordinate.
 */
export function toEdgeId(source: NodeId, target: NodeId): EdgeIdString {
    return `${source},${target}`;
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
 * Initializes an empty execution graph topology with neighborhood indexing.
 */
export function initGraph<T, N, E>(
    nodes: Node<T, N>[] = [],
    edges: Map<EdgeIdString, Edge<E>> = new Map(),
): DirectedGraph<T, N, E> {
    const successors = new Map<NodeId, Set<NodeId>>();
    const predecessors = new Map<NodeId, Set<NodeId>>();

    // Initialize tracking buckets for pre-loaded nodes
    for (const node of nodes) {
        successors.set(node.id, new Set());
        predecessors.set(node.id, new Set());
    }

    // Sync index arrays if pre-populated records are fed into initializer
    for (const edge of edges.values()) {
        if (!successors.has(edge.source))
            successors.set(edge.source, new Set());
        if (!predecessors.has(edge.target))
            predecessors.set(edge.target, new Set());

        successors.get(edge.source)!.add(edge.target);
        predecessors.get(edge.target)!.add(edge.source);
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
    return graph.nodes[id]?.type;
}

/**
 * Resolves a directed edge connection interface bridging a source and target transition point.
 */
export function getEdge<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    source: NodeId,
    target: NodeId,
): Edge<E> | undefined {
    return graph.edges.get(toEdgeId(source, target));
}

/**
 * Returns an ordered array of children node identifiers connected directly from a parent node.
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
 */
export function parentsOf<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    childId: NodeId,
): NodeId[] {
    const sources = graph.predecessors.get(childId);
    return sources ? Array.from(sources).sort((a, b) => a - b) : [];
}

/**
 * Filters downstream child elements matching a specific structural type discriminant.
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
// WRITE & MUTATION UTILITIES
// =============================================================================

/**
 * Adds a vertex node to the graph layout.
 */
export function addNode<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    token: string,
    type: T,
    label: NodeLabel,
    data: N,
): [DirectedGraph<T, N, E>, Node<T, N>] {
    const nextId = graph.nodes.length;
    const newNode: Node<T, N> = { id: nextId, token, type, label, data };

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
 */
export function addEdge<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    source: NodeId,
    target: NodeId,
    data: E,
): [DirectedGraph<T, N, E>, Edge<E>] {
    const key = toEdgeId(source, target);
    const newEdge: Edge<E> = { source, target, data };

    const nextEdges = new Map(graph.edges);
    nextEdges.set(key, newEdge);

    const nextSuccessors = new Map(graph.successors);
    const nextPredecessors = new Map(graph.predecessors);

    if (!nextSuccessors.has(source)) nextSuccessors.set(source, new Set());
    nextSuccessors.get(source)!.add(target);

    if (!nextPredecessors.has(target)) nextPredecessors.set(target, new Set());
    nextPredecessors.get(target)!.add(source);

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
 * Updates data payload on a directional edge between source and target.
 */
export function updateEdgeData<T, N, E>(
    graph: DirectedGraph<T, N, E>,
    source: NodeId,
    target: NodeId,
    newData: E,
): DirectedGraph<T, N, E> {
    const key = toEdgeId(source, target);
    if (!graph.edges.has(key)) return graph;

    const nextEdges = new Map(graph.edges);
    nextEdges.set(key, { source, target, data: newData });

    return {
        nodes: graph.nodes,
        edges: nextEdges,
        successors: graph.successors,
        predecessors: graph.predecessors,
    };
}

// =============================================================================
// SERIALIZATION HELPERS
// =============================================================================

/**
 * Exports the DirectedGraph topology into a flat, canonical LoadedGraphDict object.
 */
export function toLoadedGraphDict<T, N, E>(
    graph: DirectedGraph<T, N, E>,
): LoadedGraphDict<T, N, E> {
    return {
        nodes: graph.nodes,
        edges: Array.from(graph.edges.values()),
    };
}
