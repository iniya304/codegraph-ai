from codegraph.graph import build_call_graph, compute_impact

SAMPLE_SOURCE = '''
def a():
    return b()

def b():
    return c()

def c():
    return 1

def d():
    return 42
'''


def test_build_call_graph():
    graph = build_call_graph(SAMPLE_SOURCE)

    assert graph["a"] == ["b"]
    assert graph["b"] == ["c"]
    assert graph["c"] == []
    assert graph["d"] == []


def test_build_call_graph_syntax_error():
    assert build_call_graph("def broken(:") == {}


def test_compute_impact_direct_and_transitive():
    graph = build_call_graph(SAMPLE_SOURCE)

    result = compute_impact(graph, ["c"])

    assert result["changed"] == ["c"]
    assert result["impacted"] == ["a", "b"]


def test_compute_impact_no_callers():
    graph = build_call_graph(SAMPLE_SOURCE)

    result = compute_impact(graph, ["d"])

    assert result["impacted"] == []