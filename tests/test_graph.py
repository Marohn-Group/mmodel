"""Test GraphModel class

test cases:

1. `test_default_mockgraph` - test if the default graph matches
    the same one generated using `networkx.DiGraph`
2. `test_add_nodes` - test `add_node` and `add_nodes_from` method
3. `test_add_nodes_fails` - test if exception raise when node attribute
    not provided
4. `test_add_edges` - test `add_edge` and `add_edges_from` method
5. `test_add_edges_fails_nodes` - test if `add_edge`, `add_edges_from` raise
    exception when nodes are not defined
6. `test_add_edges_fails_attrs` - test if `add_edge`, `add_edges_from` raise
    exception when edge attribute is not defined
7. "test_copy" - test graph copy option

8-11 are modified from networkx.classes.tests.test_graph
8. "test_str_named" - test string value of the graph
9. "test_graph_chain" - test graph chain
10. "test_subgraph" - test if subgraph generate the correct view
11. "test_subgraph_copy" - test if copy subgraph create a copy of subgraph
"""


import pytest
from inspect import signature
from tests.conftest import graphs_equal


def test_node(mmodel_G):
    mmodel_G.copy()


def test_default_mockgraph(mmodel_G, standard_G):
    """Test if default ModelGraph matches the ones created by DiGraph"""

    # assert graph equal
    graphs_equal(mmodel_G, standard_G)


def test_add_nodes(mmodel_G, standard_G):
    """Test add_node and add_nodes_from methods

    The result three graph graph_a, graph_b and standard_G
    should be the same.
    """

    def mock_func(a, b):
        return a, b

    sig = signature(mock_func)
    graph_a = mmodel_G.copy()
    graph_b = mmodel_G.copy()

    graph_a.add_node("mock_func", node_obj=mock_func, return_params=["a", "b"])
    graph_b.add_nodes_from(
        [("mock_func", {"node_obj": mock_func, "return_params": ["a", "b"]})]
    )

    standard_G.add_node(
        "mock_func",
        node_obj=mock_func,
        return_params=["a", "b"],
        signature=sig,
        node_type="callable",
    )

    # assert graph equal
    graphs_equal(graph_a, graph_b)
    graphs_equal(graph_a, standard_G)


def test_add_nodes_fails(mmodel_G):
    """Test if add_nodes_from method fails when missing attributes"""

    # missing attributes
    with pytest.raises(Exception, match="Node list missing node attributes"):
        mmodel_G.add_nodes_from([("mock_func")])
    with pytest.raises(Exception, match="Node list missing attribute node_obj or return_params"):
        mmodel_G.add_nodes_from([("mock_func", {})])


def test_add_nodes_object_type_fails(mmodel_G):

    # node object should be a callable
    with pytest.raises(Exception, match="Node object type <class 'str'> not supported"):
        mmodel_G.add_node("mock_func", "obj", [])
    with pytest.raises(Exception, match="Node object type <class 'str'> not supported"):
        mmodel_G.add_nodes_from([("mock_func", {"node_obj": "obj", "return_params": []})])


def test_add_edges(mmodel_G, standard_G):
    """Test add_edge and add_edges_from methods

    The result three graph graph_a, graph_b and standard_G
    should be the same.
    """

    graph_a = mmodel_G.copy()
    graph_b = mmodel_G.copy()

    graph_a.add_edge("add", "poly", interm_params=["c"])
    graph_b.add_edges_from([("add", "poly", {"interm_params": ["c"]})])
    standard_G.add_edge("add", "poly", interm_params=["c"])

    # assert graph equal
    graphs_equal(graph_a, graph_b)
    graphs_equal(graph_a, standard_G)


@pytest.mark.parametrize(
    "edge", [("add", "mock_func", ["c"]), ("mock_func", "add", ["c"])]
)
def test_add_edge_fails_nodes(mmodel_G, edge):
    """Test if `add_edge`, `add_edges_from` fails when edge nodes are not defined"""

    with pytest.raises(Exception, match="Node mock_func is not defined"):
        mmodel_G.add_edge(*edge)


@pytest.mark.parametrize(
    "edge_list",
    [
        [("mock_func", "add", {"interm_params": ["c"]})],
        [("add", "mock_func", {"interm_params": ["c"]})],
    ],
)
def test_add_edges_from_fails_nodes(mmodel_G, edge_list):
    """Test if `add_edge`, `add_edges_from` fails when edge nodes are not defined"""

    with pytest.raises(Exception, match="Node mock_func is not defined"):
        mmodel_G.add_edges_from(edge_list)

def test_add_edges_fails_nodes(mmodel_G):
    """Test if `add_edge`, `add_edges_from` fails when missing edge attributes"""

    with pytest.raises(Exception):
        mmodel_G.add_edges_from([("add", "poly")])
    with pytest.raises(Exception, match="Edge attribute interm_params not defined"):
        mmodel_G.add_edges_from([("add", "poly", {})])


def test_copy(mmodel_G):
    """Test if copy works with MGraph"""

    graphs_equal(mmodel_G.copy(), mmodel_G)


"""The following tests are modified based on networkx.classes.tests"""


def test_str_named(mmodel_G):
    """Test the string value"""
    assert (
        str(mmodel_G)
        == f"{type(mmodel_G).__name__} named 'test' with 5 nodes and 5 edges"
    )


def test_graph_chain(mmodel_G):
    """Test Chain graph"""

    G = mmodel_G
    DG = G.to_directed(as_view=True)
    SDG = DG.subgraph(["subtract", "poly"])
    RSDG = SDG.reverse(copy=False)
    assert G is DG._graph
    assert DG is SDG._graph
    assert SDG is RSDG._graph


def test_subgraph(mmodel_G):
    """Test subgraph view"""
    G = mmodel_G

    # full subgraph
    H = G.subgraph(["add", "multiply", "subtract", "poly", "log"])
    graphs_equal(H, G)  # check if they are the same

    # partial subgraph
    H = G.subgraph(["subtract"])
    assert H.adj == {"subtract": {}}
    assert H._graph == G  # original graph

    # partial subgraph
    H = G.subgraph(["subtract", "poly"])
    assert H.adj == {"subtract": {"poly": {"interm_params": ["e"]}}, "poly": {}}
    assert H._graph == G  # original graph

    # empty subgraph
    H = G.subgraph([])
    assert H.adj == {}
    assert G.adj != {}
    assert H._graph == G  # original graph


def test_subgraph_copy(mmodel_G):
    """Test the copy of subgraph is no longer a view of original"""

    G = mmodel_G
    H = G.subgraph(["subtract", "poly"]).copy()

    assert H.adj == {"subtract": {"poly": {"interm_params": ["e"]}}, "poly": {}}

    H.remove_node("poly")
    assert "poly" in G
    # not exactly sure how to test this
    assert not hasattr(H, "_graph")
