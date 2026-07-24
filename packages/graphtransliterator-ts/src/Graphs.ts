// src/Graphs.ts

import type {
	Edge,
	LoadedGraphDict,
	Node,
	NodeId,
	NodeLabel,
} from "./types.js";

// =============================================================================
// DIRECTED GRAPH CLASS (Shared 1:1 with Python DirectedGraph)
// =============================================================================

/**
 * A directed graph representation storing nodes and edges in a flat structure.
 */
export class DirectedGraph<
	T = unknown,
	N = Record<string, unknown>,
	E = Record<string, unknown>,
> {
	public nodes: Node<T, N>[];
	public edges: Edge<E>[];

	constructor(nodes?: Node<T, N>[], edges?: Edge<E>[]) {
		this.nodes = nodes ? [...nodes] : [];
		this.edges = edges ? [...edges] : [];
	}

	/**
	 * Append a node to the graph and return its generated integer NodeId.
	 */
	public addNode(
		data: N | null = null,
		token: string | null = null,
		label: NodeLabel | null = null, // Swapped to 3rd position
		type: T | null = null, // Moved to 4th position
		extraProps: Record<string, unknown> = {},
	): NodeId {
		const nextId: NodeId = this.nodes.length;

		const newNode: Node<T, N> = {
			id: nextId,
			token,
			type: type as T,
			label,
			data: (data ?? {}) as N,
			...extraProps,
		};

		this.nodes.push(newNode);
		return nextId;
	}
	/**
	 * Return node by numeric NodeId if present.
	 */
	public getNode(nodeId: NodeId): Node<T, N> | null {
		if (nodeId >= 0 && nodeId < this.nodes.length) {
			return this.nodes[nodeId];
		}
		return null;
	}

	/**
	 * Add a directed edge connecting a source NodeId to a target NodeId.
	 */
	public addEdge(source: NodeId, target: NodeId, data: E | null = null): void {
		if (!Number.isInteger(source) || !Number.isInteger(target)) {
			throw new Error("Source and target node indices must be integers.");
		}

		if (
			source < 0 ||
			source >= this.nodes.length ||
			target < 0 ||
			target >= this.nodes.length
		) {
			throw new Error(
				`Source node ${source} or target node ${target} not found in graph.`,
			);
		}

		const actualData: E = (
			data !== null && typeof data === "object" ? { ...data } : {}
		) as E;

		const newEdge: Edge<E> = {
			source,
			target,
			data: actualData,
		};

		this.edges.push(newEdge);
	}

	/**
	 * Return the edge payload or full edge structure connecting source and target.
	 */
	public getEdge(source: NodeId, target: NodeId): E | Edge<E> | null {
		for (const edge of this.edges) {
			if (edge.source === source && edge.target === target) {
				const data = edge.data;
				if (data && typeof data === "object" && !Array.isArray(data)) {
					return data;
				}
				return edge;
			}
		}
		return null;
	}

	/**
	 * Return a list of all edge connection coordinates as [source, target] tuples.
	 */
	public get edgeList(): Array<[NodeId, NodeId]> {
		return this.edges.map((edge) => [edge.source, edge.target]);
	}

	/**
	 * Export graph layout as canonical flat dictionary matching Python.
	 */
	public toDict(): LoadedGraphDict<T, N, E> {
		return {
			nodes: this.nodes,
			edges: this.edges,
		};
	}
}

// =============================================================================
// COVERAGE LOGGING & TRACKING EXTENSIONS
// =============================================================================

/**
 * Subclass monitoring runtime traversal over nodes and edges.
 */
export class VisitLoggingDirectedGraph<
	T = unknown,
	N = Record<string, unknown>,
	E = Record<string, unknown>,
> extends DirectedGraph<T, N, E> {
	public visitedNodes: Set<NodeId>;
	public visitedEdges: Set<string>; // Stored as "source->target" string keys

	constructor(graph: DirectedGraph<T, N, E>) {
		super(graph.nodes, graph.edges);
		this.visitedNodes = new Set<NodeId>();
		this.visitedEdges = new Set<string>();
	}

	/**
	 * Log traversal of a node.
	 */
	public visitNode(nodeId: NodeId): void {
		this.visitedNodes.add(nodeId);
	}

	/**
	 * Log traversal of an edge connection.
	 */
	public visitEdge(source: NodeId, target: NodeId): void {
		this.visitedEdges.add(`${source}->${target}`);
	}

	/**
	 * Reset tracked graph metadata.
	 */
	public clearVisited(): void {
		this.visitedNodes.clear();
		this.visitedEdges.clear();
	}

	/**
	 * Validate if all edges in graph configuration were traversed.
	 */
	public checkCoverage(raiseException: boolean = true): boolean {
		const missingEdges: Array<[NodeId, NodeId]> = [];

		for (const [source, target] of this.edgeList) {
			if (!this.visitedEdges.has(`${source}->${target}`)) {
				console.warn(
					`Edge (${source} -> ${target}) was never visited during runtime.`,
				);
				missingEdges.push([source, target]);
			}
		}

		if (missingEdges.length > 0 && raiseException) {
			const edgeStr = missingEdges.map(([u, v]) => `${u}->${v}`).join(", ");
			throw new Error(`Incomplete graph edge coverage: ${edgeStr}`);
		}

		return missingEdges.length === 0;
	}
}
