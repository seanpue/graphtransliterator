import { describe, expect, it } from "vitest";
import { DirectedGraph } from "../src/Graphs";

describe("Graphs Topology Framework", () => {
	it("should initialize an empty graph topology cleanly", () => {
		const graph = new DirectedGraph<string, { value: string }, number>();

		expect(graph.nodes).toHaveLength(0);
		expect(graph.edges).toHaveLength(0);
		expect(graph.edgeList).toEqual([]);
	});

	it("should support stateful node insertion and assign sequential IDs", () => {
		const graph = new DirectedGraph<string, { weight: number }, null>();

		// Add first node
		const nodeAId = graph.addNode({ weight: 10 }, "STATE", "NodeA");
		expect(nodeAId).toBe(0);
		expect(graph.getNode(0)?.label).toBe("NodeA");
		expect(graph.getNode(0)?.data.weight).toBe(10);

		// Add second node
		const nodeBId = graph.addNode({ weight: 20 }, "ACCEPT", "NodeB");
		expect(nodeBId).toBe(1);
		expect(graph.nodes).toHaveLength(2);
	});

	it("should establish directional edges and retrieve edge connections", () => {
		const graph = new DirectedGraph<
			string,
			Record<string, unknown>,
			{ label: string }
		>();

		// Setup two nodes
		const nodeAId = graph.addNode({}, "V", "A");
		const nodeBId = graph.addNode({}, "V", "B");

		// Wire an edge connecting node 0 -> node 1
		graph.addEdge(nodeAId, nodeBId, { label: "transition-payload" });

		expect(graph.edges).toHaveLength(1);
		expect(graph.edgeList).toEqual([[nodeAId, nodeBId]]);

		// Verify edge payload lookup
		const edgePayload = graph.getEdge(nodeAId, nodeBId);
		expect(edgePayload).toEqual({ label: "transition-payload" });
	});

	it("should safely retrieve nodes and update payload properties directly", () => {
		const graph = new DirectedGraph<string, { score: number }, null>();

		const nodeId = graph.addNode({ score: 100 }, "META", "Target");

		const node = graph.getNode(nodeId);
		expect(node).not.toBeNull();

		if (node) {
			node.data.score += 50;
		}

		// Ensure stateful node modification is reflected in graph reference
		expect(graph.getNode(nodeId)?.data.score).toBe(150);
	});

	it("should throw errors when attempting to add edges to invalid node indices", () => {
		const graph = new DirectedGraph();

		graph.addNode({}, "V", "A");

		// Out of bounds target node
		expect(() => graph.addEdge(0, 99)).toThrowError(
			"Source node 0 or target node 99 not found in graph.",
		);
	});
});
