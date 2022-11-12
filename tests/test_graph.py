from tests.conftest import graph_equal
from mmodel import ModelGraph, draw_graph, modifier
import pytest
from functools import wraps
from networkx import DiGraph
from inspect import signature


class TestAddEdge:
    """Test add_edge and add_grouped_edges_from"""

    @pytest.fixture
    def base_G(self):
        """Base ModelGraph with pre-defined nodes"""

        def func_a(m, n):
            return m + n

        def func_b(o):
            return 2 * o

        def func_c(o, s):
            return o + s

        def func_d(t, w):
            return t + w

        G = ModelGraph()
        G.add_node("func_a", func=func_a, output="o", sig=signature(func_a))
        G.add_node("func_b", func=func_b, output="q", sig=signature(func_b))
        G.add_node("func_c", func=func_c, output="t", sig=signature(func_c))
        G.add_node("func_d", func=func_d, output="x", sig=signature(func_d))

        return G

    def test_add_edge(self, base_G):
        """Test add_edge updates the edge variable"""

        base_G.add_edge("func_a", "func_b")

        assert base_G.edges["func_a", "func_b"]["val"] == "o"

    def test_add_edges_from(self, base_G):
        """Test add_edges_from updates the graph and edge variable"""

        base_G.add_edges_from([["func_a", "func_b"], ["func_a", "func_c"]])

        assert base_G.edges["func_a", "func_b"]["val"] == "o"
        assert base_G.edges["func_a", "func_c"]["val"] == "o"

    def test_add_grouped_edge_without_list(self, base_G):
        """Test add_grouped_edge

        The grouped edge allows similar behavior as DiGraph.add_edge
        """

        base_G.add_grouped_edge("func_a", "func_b")

        assert base_G.edges["func_a", "func_b"]["val"] == "o"

    def test_add_grouped_edge_with_list(self, base_G):
        """Test add_grouped_edge

        The grouped edge should allow list node inputs
        """
        base_G.add_grouped_edge("func_a", ["func_b", "func_c"])
        base_G.add_grouped_edge(["func_b", "func_c"], "func_d")

        assert [
            ("func_a", "func_b"),
            ("func_a", "func_c"),
            ("func_b", "func_d"),
            ("func_c", "func_d"),
        ] == list(base_G.edges)

    def test_add_grouped_edge_fails(self, base_G):
        """Test add_grouped_edge

        The method raises exception when u and v are both lists.
        """

        with pytest.raises(Exception, match="only one edge node can be a list"):
            base_G.add_grouped_edge(["func_a", "func_b"], ["func_c", "func_d"])


class TestSetNodeObject:
    """Test set_node_object and set_node_objects_from"""

    @pytest.fixture
    def base_G(self):
        """Basic ModelGraph with pre defined edges"""

        def func_a(m, n):
            return m + n

        G = ModelGraph()
        G.add_edge("func_a", "func_b")
        G.add_edge("func_a", "func_c")

        def modifier(func, value):
            """Basic modifier"""

            @wraps(func)
            def wrapper(**kwargs):
                return func(**kwargs) + value

            return wrapper

        G.set_node_object(
            "func_a",
            func_a,
            "o",
            inputs=["a", "b"],
            modifiers=[(modifier, {"value": 1})],
        )

        return G

    def test_set_node_object(self, base_G):
        """Test node basic attributes"""

        assert base_G.nodes["func_a"]["base_func"].__name__ == "func_a"
        assert base_G.nodes["func_a"]["output"] == "o"

    def test_set_node_object_inputs(self, base_G):
        """Test node signatures are updated"""

        assert list(base_G.nodes["func_a"]["sig"].parameters.keys()) == ["a", "b"]

    def test_set_node_object_modifiers(self, base_G):
        """Test node modifiers are applied and in correct order"""

        assert (
            base_G.nodes["func_a"]["modifiers"][0][0].__name__ == "signature_modifier"
        )
        assert base_G.nodes["func_a"]["modifiers"][1][0].__name__ == "modifier"

    def test_set_node_object_base_func(self, base_G):
        """Test that the base function is not changed"""

        assert base_G.nodes["func_a"]["base_func"](m=1, n=2) == 3

    def test_set_node_object_modified_func(self, base_G):
        """Test the final node function has the correct signature and output"""

        assert base_G.nodes["func_a"]["func"](a=1, b=2) == 4

    def test_set_node_objects_from(self, base_G):
        """Test set_node_objects_from method

        Test if the edge attributes are updated
        """

        def func_b(o, p):
            return o + p

        def func_c(o, s):
            return o + s

        base_G.set_node_objects_from(
            [("func_b", func_b, ["q"]), ("func_c", func_c, ["t"])]
        )

        assert base_G.edges["func_a", "func_b"] == {"val": "o"}
        assert base_G.edges["func_a", "func_c"] == {"val": "o"}


class TestModelGrapahFunc:
    """Test node object input for builtin func and ufunc"""

    @pytest.fixture
    def base_G(self):
        """Basic ModelGraph with pre defined edges"""

        import numpy as np
        import math

        G = ModelGraph()
        G.add_edge("func_a", "func_b")

        G.set_node_object("func_a", np.add, "x", inputs=["a", "b"])
        G.set_node_object("func_b", math.ceil, "p", inputs=["x"])

        return G

    def test_signature(self, base_G):
        """Test signature of the graph nodes"""
        assert list(base_G.nodes["func_a"]["sig"].parameters.keys()) == ["a", "b"]
        assert list(base_G.nodes["func_b"]["sig"].parameters.keys()) == ["x"]


class TestModelGraphBasics:
    """Test the basic string and repr of the graph and nodes"""

    def test_networkx_equality(self, mmodel_G, standard_G):
        """Test if ModelGraph instance matches the ones created by networkx.DiGraph"""

        assert graph_equal(mmodel_G, standard_G)

    def test_graph_name(self, mmodel_G):
        """Test naming and docs of the graph"""

        assert mmodel_G.name == "test graph"

    def test_graph_str(self, mmodel_G):
        """Test graph representation"""

        assert str(mmodel_G) == "ModelGraph named 'test graph' with 5 nodes and 5 edges"

    def test_view_node(self, mmodel_G):
        """Test if view node outputs node information correctly"""

        log_s = "log\n  callable: logarithm(c, b)\n  return: m\n  modifiers: []"

        assert mmodel_G.view_node("log") == log_s

    def test_view_node_with_modifiers(self, mmodel_G):
        """Test if view node outputs node information correctly"""

        def func(a, b):
            return a + b

        def modifier(func, value):
            return func

        mmodel_G.add_node("test_node")
        mmodel_G.set_node_object(
            "test_node",
            func,
            "c",
            [],
            [(modifier, {"value": 1}), (modifier, {"value": 2})],
        )

        assert (
            "modifiers: [modifier, {'value': 1}, modifier, {'value': 2}]"
            in mmodel_G.view_node("test_node")
        )

    def test_draw(self, mmodel_G):
        """Test the draw method of ModelGraph instance

        The draw methods are tested in test_draw module. Here we make sure
        the label is correct. The repr escapes \n, therefore the string is used to compare
        """
        dot_graph = mmodel_G.draw(draw_graph)
        label = """label="ModelGraph named \'test graph\' with 5 nodes and 5 edges"""
        assert label in dot_graph.source


class TestGraphOperation:
    """Test the copy, deepcopy, chain, subgraph, subgraph copy based on networkx"""

    def test_copy(self, mmodel_G):
        """Test if copy works with ModelGraph"""

        assert graph_equal(mmodel_G.copy(), mmodel_G)
        assert mmodel_G.copy().graph is not mmodel_G.graph

    def test_deepcopy(self, mmodel_G):
        """Test if copy creates a new graph attribute dictionary"""

        G_deepcopy = mmodel_G.deepcopy()
        G_copy = mmodel_G.copy()

        # check if graph is correctly duplicated
        assert graph_equal(G_deepcopy, mmodel_G)
        assert G_copy.graph == G_deepcopy.graph
        # see test_copy that the two dictionaries are the same
        assert G_deepcopy.graph is not mmodel_G.graph

        assert G_copy.graph is not G_deepcopy.graph

    def test_graph_chain(self, mmodel_G):
        """Test Chain graph"""

        G = mmodel_G
        DG = G.to_directed(as_view=True)
        SDG = DG.subgraph(["subtract", "poly"])
        RSDG = SDG.reverse(copy=False)
        assert G is DG._graph
        assert DG is SDG._graph
        assert SDG is RSDG._graph

    def test_subgraph(self, mmodel_G):
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
        assert H.adj == {"subtract": {"multiply": {"val": "e"}}, "multiply": {}}
        assert H._graph == G  # original graph

        # empty subgraph
        H = G.subgraph([])
        assert H.adj == {}
        assert G.adj != {}
        assert H._graph == G  # original graph

    def test_subgraph_deepcopy(self, mmodel_G):
        """Test the subgraph is copied correctly and they no longer share graph
        attributes.

        Subgraph view retains the graph attribute, and the copy method is only a
        shallow copy. Modify a copied subgraph attribute changes the original graph
        """

        H = mmodel_G.subgraph(["subtract", "multiply"]).deepcopy()

        assert H.adj == {"subtract": {"multiply": {"val": "e"}}, "multiply": {}}

        # check the graph attribute is no longer the same dictionary
        assert H.graph == mmodel_G.graph
        assert H.graph is not mmodel_G.graph

        H.name = "subgraph_test"
        assert mmodel_G.name != "subgraph_test"
