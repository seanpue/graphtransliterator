import { describe, expect, it } from "vitest";
import {
	addEdge,
	addNode,
	childrenOf,
	getNode,
	hasNode,
	initGraph,
	parentsOf,
	updateNode,
} from "../src/Graphs";

describe("Graphs Topology Framework", () => {
	it("should initialize an empty graph topology cleanly", () => {
		const graph = initGraph<string, { value: string }, number>();

		expect(graph.nodes).toHaveLength(0);
		expect(graph.edges.size).toBe(0);
		expect(graph.successors.size).toBe(0);
		expect(graph.predecessors.size).toBe(0);
	});

	it("should support immutable node insertion and assign sequential IDs", () => {
		const g0 = initGraph<string, { weight: number }, null>();

		// Add first node
		const [g1, nodeA] = addNode(g0, "STATE", "NodeA", { weight: 10 });
		expect(nodeA.id).toBe(0);
		expect(hasNode(g1, 0)).toBe(true);
		expect(getNode(g1, 0)?.label).toBe("NodeA");

		// Immutability Check: Ensure original graph g0 remained empty
		expect(g0.nodes).toHaveLength(0);

		// Add second node
		const [g2, nodeB] = addNode(g1, "ACCEPT", "NodeB", { weight: 20 });
		expect(nodeB.id).toBe(1);
		expect(g2.nodes).toHaveLength(2);
	});

	it("should establish directional edges and build O(1) tracking indexes", () => {
		const graph = initGraph<string, null, string>();

		// Setup two nodes

		const [graph1, nodeA] = addNode(graph, "V", "A", null);
		const [finalGraph, nodeB] = addNode(graph1, "V", "B", null);

		// Wire an edge connecting node 0 -> node 1
		const [nextGraph, _edge] = addEdge(
			finalGraph,
			nodeA.id,
			nodeB.id,
			"transition-payload",
		);

		expect(nextGraph.edges.size).toBe(1);
		expect(childrenOf(nextGraph, nodeA.id)).toEqual([nodeB.id]);
		expect(parentsOf(nextGraph, nodeB.id)).toEqual([nodeA.id]);
	});

	it("should safely update a target node payload without mutating state history", () => {
		const graph = initGraph<string, { score: number }, null>();

		const [graph1, node] = addNode(graph, "META", "Target", { score: 100 });

		const updatedGraph = updateNode(graph1, node.id, (oldData) => ({
			score: oldData.score + 50,
		}));

		// Ensure the new graph configuration contains the modifications
		expect(getNode(updatedGraph, node.id)?.data.score).toBe(150);

		// FIX: Verify against graph1 (the state prior to the update target operation)
		expect(getNode(graph1, node.id)?.data.score).toBe(100);
	});
});
