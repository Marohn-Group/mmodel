from tests.conftest import graph_equal
from mmodel import ModelGraph, draw_graph
import pytest
from functools import wraps

GRAPH_REPR = "ModelGraph named 'test graph' with 5 nodes and 5 edges"


def test_default_mockgraph(mmodel_G, standard_G):
    """Test if default ModelGraph matches the ones created by DiGraph"""

    # assert graph equal
    assert graph_equal(mmodel_G, standard_G)


def test_graph_name(mmodel_G):
    """Test naming and docs of the graph"""
    assert mmodel_G.name == "test graph"


def test_graph_str(mmodel_G):
    """Test graph representation"""

    assert str(mmodel_G) == GRAPH_REPR


def test_set_node_object():
    """Test add node objects"""

    def func_a(a, b):
        return None

    def func_b(c, d):
        return None

    G = ModelGraph()
    G.add_edge("node_a", "node_b")
    G.set_node_object("node_a", func_a, ["c"])
    assert G.nodes["node_a"]["returns"] == ["c"]
    assert "sig" in G.nodes["node_a"]

    # test the edges are updated
    assert G.edges["node_a", "node_b"] == {}
    G.set_node_object("node_b", func_b, ["e"])
    assert G.edges["node_a", "node_b"] == {"val": ["c"]}


def test_set_node_object_modifiers():
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
    G.add_node("node_a")
    G.set_node_object("node_a", func_a, ["c"], [], modifiers=[(mod_method, {})])

    func = G.nodes["node_a"]["func"]

    assert func(a=1, b=2) == 4


def test_set_node_object_input():
    """Test behavior when inputs are added along with the modifiers

    The signature modifier should always be the first modifier
    """

    def func_a(a, b):
        return a + b

    def mod_method(func):
        @wraps(func)
        def wrapper(**kwargs):
            return func(**kwargs) + 1

        return wrapper

    G = ModelGraph()
    G.add_node("node_a")
    G.set_node_object("node_a", func_a, ["c"], ["d", "e"], modifiers=[(mod_method, {})])

    func = G.nodes["node_a"]["func"]

    assert G.nodes["node_a"]["modifiers"][0][0].__name__ == "signature_modifier"
    assert func(d=1, e=2) == 4


def test_set_node_objects_from():
    """Test set_node_objects_from method

    Test if the edge attributes are updated
    """

    def func_a(a, b):
        return None

    def func_b(c, d):
        return None

    G = ModelGraph()
    G.add_edge("node_a", "node_b")
    G.set_node_objects_from([("node_a", func_a, ["c"]), ("node_b", func_b, ["e"])])

    assert G.edges["node_a", "node_b"] == {"val": ["c"]}


def test_set_node_objects_from_modifiers():
    """Test set_node_objects_from method with modifiers added to some nodes

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
    G.set_node_objects_from(
        [("node_a", func_a, ["c"], [], [(mod_method, {})]), ("node_b", func_b, ["e"])]
    )

    assert G.nodes["node_a"]["func"](a=1, b=2) == 4
    assert G.nodes["node_b"]["func"](1, 2) == (1, 2)


def test_add_edge(mmodel_G):
    """Test add_edge updates the graph"""

    def func_a(m, b):
        return None

    mmodel_G.add_node("func_a")
    mmodel_G.set_node_object("func_a", func_a, ["n"])
    mmodel_G.add_edge("log", "func_a")

    assert mmodel_G.edges["log", "func_a"]["val"] == ["m"]


def test_add_edges_from(mmodel_G):
    """Test add_edges_from updates the graph"""

    def func_a(c, m):
        return None

    mmodel_G.add_node("func_a")
    mmodel_G.set_node_object("func_a", func_a, ["n"])
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
    """Test if copy works with ModelGraph

    See networkx issue
    """

    assert graph_equal(mmodel_G.copy(), mmodel_G)
    assert mmodel_G.copy().graph is not mmodel_G.graph


def test_deepcopy(mmodel_G):
    """Test if copy creates a new graph attribute dictionary"""
    G_deepcopy = mmodel_G.deepcopy()
    G_copy = mmodel_G.copy()

    # check if graph is correctly duplicated
    assert graph_equal(G_deepcopy, mmodel_G)
    assert G_copy.graph == G_deepcopy.graph
    # see test_copy that the two dictionaries are the same
    assert G_deepcopy.graph is not mmodel_G.graph

    assert G_copy.graph is not G_deepcopy.graph


NODE_STR = """log node
  callable: logarithm(c, b)
  returns: m
  modifiers: []"""


def test_view_node_without_modifiers(mmodel_G):
    """Test if view node outputs node information correctly"""

    assert mmodel_G.view_node("log") == NODE_STR


def test_view_node_with_modifiers(mmodel_G):
    """Test if view node outputs node information correctly"""

    def func(a, b):
        return a + b

    def mockmod(func):
        return func

    mmodel_G.add_node("test_node")
    mmodel_G.set_node_object(
        "test_node", func, ["c"], [], [(mockmod, {}), (mockmod, {})]
    )

    assert "modifiers: [mockmod, {}, mockmod, {}]" in mmodel_G.view_node("test_node")


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
    assert graph_equal(H, G)  # check if they are the same

    # partial subgraph
    H = G.subgraph(["subtract"])
    assert H.adj == {"subtract": {}}
    assert H._graph == G  # original graph

    # partial subgraph
    H = G.subgraph(["subtract", "multiply"])
    assert H.adj == {"subtract": {"multiply": {"val": ["e"]}}, "multiply": {}}
    assert H._graph == G  # original graph

    # empty subgraph
    H = G.subgraph([])
    assert H.adj == {}
    assert G.adj != {}
    assert H._graph == G  # original graph


def test_subgraph_deepcopy(mmodel_G):
    """Test the subgraph is copied correctly and they no longer share graph
    attributes.

    Subgraph view retains the graph attribute, and the copy method is only a
    shallow copy. Modify a copied subgraph attribute changes the original graph
    """

    H = mmodel_G.subgraph(["subtract", "multiply"]).deepcopy()

    assert H.adj == {"subtract": {"multiply": {"val": ["e"]}}, "multiply": {}}

    # check the graph attribute is no longer the same dictionary
    assert H.graph == mmodel_G.graph
    assert H.graph is not mmodel_G.graph

    H.name = "subgraph_test"
    assert mmodel_G.name != "subgraph_test"


"""label with quotation mark escaped"""

ESC_LABEL = """label="ModelGraph named \'test graph\' with 5 nodes and 5 edges"""


def test_draw(mmodel_G):
    """Test the draw method of ModelGraph instance

    The draw methods are tested in test_draw module. Here we make sure
    the label is correct. The repr escapes \n, therefore the string is used to compare
    """
    dot_graph = mmodel_G.draw(draw_graph)

    assert ESC_LABEL in dot_graph.source
