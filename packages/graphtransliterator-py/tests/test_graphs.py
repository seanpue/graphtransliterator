from graphtransliterator.graphs import DirectedGraph, OnMatchRuleProxy, VisitLoggingList


def test_directed_graph_edge_cases():
    graph = DirectedGraph()
    graph.add_node({"type": "A"})
    graph.add_node({"type": "B"})
    graph.add_edge(0, 1, {"cost": 1})

    # Test representation / string formatting
    assert repr(graph)

    # Test edge/node retrieval error cases or removal
    assert graph.get_edge(0, 1) == {"cost": 1}
    assert graph.get_edge(1, 0) is None

    # Check graph equality / dict conversions if implemented
    graph_dict = graph.to_dict() if hasattr(graph, "to_dict") else None
    if graph_dict:
        assert "nodes" in graph_dict


def test_directed_graph_non_dict_edge_data_and_edge_list():
    graph = DirectedGraph()
    graph.add_node(data={"type": "A"})
    graph.add_node(data={"type": "B"})

    # Manually append an edge with non-dict data to test line 94
    graph.edges.append({"source": 0, "target": 1, "data": "non_dict_data"})

    # Test line 94: returns full edge dict when data is not a dict
    edge = graph.get_edge(0, 1)
    assert edge == {"source": 0, "target": 1, "data": "non_dict_data"}

    # Test line 102: edge_list property
    assert graph.edge_list == [(0, 1)]


def test_graph_get_node_out_of_bounds():
    g = DirectedGraph()
    assert g.get_node(999) is None


def test_directed_graph_get_edge_and_out_of_bounds():
    g = DirectedGraph()
    n1 = g.add_node(token="a")
    n2 = g.add_node(token="b")
    g.add_edge(n1, n2, data={"cost": 1})

    # Test get_edge hit and miss
    edge_data = g.get_edge(n1, n2)
    assert edge_data == {"cost": 1}
    assert g.get_edge(n2, n1) is None

    # Test get_node out of bounds
    assert g.get_node(999) is None


def test_on_match_rule_proxy_dunders():
    visited = set()

    # Class with 'production' attribute to satisfy hasattr(_obj, "production")
    class DummyRuleObj:
        def __init__(self):
            self.production = "X"
            self.val = 100

        def __getitem__(self, item):
            return getattr(self, item)

        def __len__(self):
            return 2

    rule_obj = DummyRuleObj()
    proxy = OnMatchRuleProxy(rule_obj, 0, visited)

    assert len(proxy) == 2
    assert repr(proxy) == repr(rule_obj)
    assert str(proxy) == str(rule_obj)

    # Accessing item matching 'production' triggers visited set
    _ = proxy["production"]
    assert 0 in visited


def test_on_match_rule_proxy_coverage():
    visited = set()

    class DummyRule:
        def __init__(self):
            self.production = "X"
            self.val = 100

        def __getitem__(self, item):
            return getattr(self, item)

    rule_obj = DummyRule()
    proxy = OnMatchRuleProxy(rule_obj, 0, visited)

    # Test getattr triggering production match on class instance
    assert proxy.production == "X"
    assert 0 in visited

    # Test setattr
    proxy.val = 200
    assert rule_obj.val == 200

    # Test item access on object with 'production' attribute
    obj_visited = set()
    obj_proxy = OnMatchRuleProxy(DummyRule(), 1, obj_visited)
    assert obj_proxy["production"] == "X"
    assert 1 in obj_visited


def test_visit_logging_list_copy_constructor():
    vlist1 = VisitLoggingList(["a", "b"])
    vlist1.visit(0)

    # Copy constructor line 150-151
    vlist2 = VisitLoggingList(vlist1)
    assert 0 in vlist2.visited
    assert vlist2.data != []
