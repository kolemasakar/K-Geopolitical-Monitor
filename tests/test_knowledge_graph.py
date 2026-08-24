from src.kgeopolitical_monitor.knowledge_graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge


def test_graph_adds_nodes_and_edges():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode('a', 'country'))
    graph.add_edge(KnowledgeEdge('a', 'b', 'influences', 0.8))
    assert 'a' in graph.nodes
    assert len(graph.edges) == 1
