from tests.conftest import assert_graphs_equal
from mmodel import ModelGraph
import pytest
from functools import wraps

GRAPH_REPR = """ModelGraph named 'test' with 5 nodes and 5 edges

test object

long description"""


def test_default_mockgraph(mmodel_G, standard_G):
    """Test if default ModelGraph matches the ones created by DiGraph"""

    # assert graph equal
    assert_graphs_equal(mmodel_G, standard_G)


def test_graph_name(mmodel_G):
    """Test naming and docs of the graph"""
    assert mmodel_G.name == "test"


def test_graph_str(mmodel_G):
    """Test graph representation"""

    assert str(mmodel_G) == GRAPH_REPR


def test_add_node_object():
    """Test add node objects"""

    def func_a(a, b):
        return None

    def func_b(c, d):
        return None

    G = ModelGraph()
    G.add_edge("node_a", "node_b")
    G.add_node_object("node_a", func_a, ["c"])
    assert G.nodes["node_a"]["returns"] == ["c"]
    assert "sig" in G.nodes["node_a"]

    # test the edges are updated
    assert G.edges["node_a", "node_b"] == {}
    G.add_node_object("node_b", func_b, ["e"])
    assert G.edges["node_a", "node_b"] == {"val": ["c"]}


def test_add_undefined_node_object():
    """Test behavior when the node is not yet defined

    Node should be added if it is not defined
    """

    def func_a(a, b):
        return None

    G = ModelGraph()
    G.add_node_object("node_a", func_a, ["c"])

    assert "node_a" in G.nodes


def test_add_node_object_modifiers():
    """Test behavior when modifiers are added to node object

    Here we mock a wrapper that changes the node result
    """

    def func_a(a, b):
        return a + b

    def mod_method(func):
        @wraps(func)
        def wrapper(**kwargs):
            return func(**kwargs) + 1

        return wrapper

    G = ModelGraph()
    G.add_node_object("node_a", func_a, ["c"], modifiers=[mod_method])

    func = G.nodes["node_a"]["obj"]

    assert func(a=1, b=2) == 4


def test_add_node_objects_from():
    """Test add_node_objects_from method

    Test if the edge attributes are updated
    """

    def func_a(a, b):
        return None

    def func_b(c, d):
        return None

    G = ModelGraph()
    G.add_edge("node_a", "node_b")
    G.add_node_objects_from([("node_a", func_a, ["c"]), ("node_b", func_b, ["e"])])

    assert G.edges["node_a", "node_b"] == {"val": ["c"]}


def test_add_node_objects_from_modifiers():
    """Test add_node_objects_from method with modifiers added to some nodes

    Test if the modifiers are properly implemented with the unzip method
    """

    def func_a(a, b):
        return a + b

    def func_b(c, d):
        return c, d

    def mod_method(func):
        @wraps(func)
        def wrapper(**kwargs):
            return func(**kwargs) + 1

        return wrapper

    G = ModelGraph()
    G.add_edge("node_a", "node_b")
    G.add_node_objects_from(
        [("node_a", func_a, ["c"], [mod_method]), ("node_b", func_b, ["e"])]
    )

    assert G.nodes["node_a"]["obj"](a=1, b=2) == 4
    assert G.nodes["node_b"]["obj"](1, 2) == (1, 2)


def test_add_edge(mmodel_G):
    """Test add_edge updates the graph"""

    def func_a(m, b):
        return None

    mmodel_G.add_node_object("func_a", func_a, ["n"])
    mmodel_G.add_edge("log", "func_a")

    assert mmodel_G.edges["log", "func_a"]["val"] == ["m"]


def test_add_edges_from(mmodel_G):
    """Test add_edges_from updates the graph"""

    def func_a(c, m):
        return None

    mmodel_G.add_node_object("func_a", func_a, ["n"])
    mmodel_G.add_edges_from([["add", "func_a"], ["log", "func_a"]])

    assert mmodel_G.edges["add", "func_a"]["val"] == ["c"]
    assert mmodel_G.edges["log", "func_a"]["val"] == ["m"]


def test_add_grouped_edge_no_list():
    """Test add_grouped_edge

    The grouped edge should allow list node inputs
    """

    G = ModelGraph()
    G.add_grouped_edge("node_a", "node_b")

    assert ["node_a", "node_b"] in G.edges


def test_add_grouped_edge_with_list():
    """Test add_grouped_edge

    The grouped edge should allow list node inputs
    """

    G = ModelGraph()
    G.add_grouped_edge(["node_a", "node_b"], "node_c")
    G.add_grouped_edge("node_c", ["node_d", "node_e"])

    assert ["node_a", "node_c"] in G.edges
    assert ["node_b", "node_c"] in G.edges
    assert ["node_c", "node_d"] in G.edges
    assert ["node_c", "node_e"] in G.edges


def test_add_grouped_edge_fails():
    """Test add_grouped_edge

    The method raises exception when u and v are
    both lists
    """

    G = ModelGraph()

    with pytest.raises(Exception, match="only one edge node can be a list"):
        G.add_grouped_edge(["node_a", "node_b"], ["node_c", "node_d"])


def test_copy(mmodel_G):
    """Test if copy works with MGraph"""

    assert_graphs_equal(mmodel_G.copy(), mmodel_G)


"""The following tests are modified based on networkx.classes.tests"""


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
    assert_graphs_equal(H, G)  # check if they are the same

    # partial subgraph
    H = G.subgraph(["subtract"])
    assert H.adj == {"subtract": {}}
    assert H._graph == G  # original graph

    # partial subgraph
    H = G.subgraph(["subtract", "poly"])
    assert H.adj == {"subtract": {"poly": {"val": ["e"]}}, "poly": {}}
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

    assert H.adj == {"subtract": {"poly": {"val": ["e"]}}, "poly": {}}

    H.remove_node("poly")
    assert "poly" in G
    # not exactly sure how to test this
    assert not hasattr(H, "_graph")
