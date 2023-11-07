from tests.conftest import graph_equal
from mmodel import Graph
from mmodel.utility import modelgraph_signature
from mmodel.node import Node
import pytest
from functools import wraps
from inspect import signature
from textwrap import dedent
import inspect


class TestAddEdge:
    """Test add_edge and add_grouped_edges_from."""

    @pytest.fixture
    def base_G(self):
        """Base Graph with pre-defined nodes."""

        def func_a(m, n):
            return m + n

        def func_b(o):
            return 2 * o

        def func_c(o, s):
            return o + s

        a_node = Node("func_a", func_a, output="o")
        b_node = Node("func_b", func_b, output="q")
        c_node = Node("func_c", func_c, output="t")

        G = Graph()
        G.add_node("func_a", node_object=a_node, output="o", signature=a_node.signature)
        G.add_node("func_b", node_object=b_node, output="q", signature=b_node.signature)
        G.add_node("func_c", node_object=c_node, output="t", signature=c_node.signature)

        return G

    def test_add_edge(self, base_G):
        """Test add_edge updates the edge variable."""

        base_G.add_edge("func_a", "func_b")

        assert base_G.edges["func_a", "func_b"]["var"] == "o"

    def test_add_edges_from(self, base_G):
        """Test add_edges_from updates the graph and edge variable."""

        base_G.add_edges_from([["func_a", "func_b"], ["func_a", "func_c"]])

        assert base_G.edges["func_a", "func_b"]["var"] == "o"
        assert base_G.edges["func_a", "func_c"]["var"] == "o"

    def test_update_edge_vals(self, base_G):
        """Test edge updates.

        The edges are not updated if:
        1. the parent edge is not defined
        1. the child edge is not defined
        2. the parent out does not match the child parameter
        """

        base_G.add_edge("func_a", "func_d")
        assert "var" not in base_G.edges["func_a", "func_d"]

        def func_d(t, w):
            return t + w

        base_G.add_node("func_d", func=func_d, output="x", sig=signature(func_d))
        assert "var" not in base_G.edges["func_a", "func_d"]

    def test_add_grouped_edge_without_list(self, base_G):
        """Test add_grouped_edge.

        The grouped edge allows similar behavior as ``DiGraph.add_edge``.
        """

        base_G.add_grouped_edge("func_a", "func_b")

        assert base_G.edges["func_a", "func_b"]["var"] == "o"

    def test_add_grouped_edge_with_list(self, base_G):
        """Test add_grouped_edge.

        The grouped edge should allow list node inputs.
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
        """Test add_grouped_edge.

        The method raises an exception when u and v are both lists.
        """

        with pytest.raises(Exception, match="only one edge node can be a list"):
            base_G.add_grouped_edge(["func_a", "func_b"], ["func_c", "func_d"])


class TestSetNodeObject:
    """Test set_node_object and set_node_objects_from."""

    @pytest.fixture
    def node(self, value_modifier):
        """Basic Graph with pre-defined edges."""

        def func_a(m, n):
            """Base function."""
            return m + n

        node_a = Node(
            "func_a",
            func_a,
            output="o",
            inputs=["a", "b"],
            modifiers=[value_modifier(value=1)],
        )

        return node_a

    @pytest.fixture
    def base_G(self, node):
        """Basic Graph with pre-defined edges."""

        G = Graph()
        G.add_edge("func_a", "func_b")
        G.add_edge("func_a", "func_c")

        G.set_node_object(node)

        return G

    def test_set_node_object(self, base_G, node):
        """Test node basic attributes."""

        assert base_G.nodes["func_a"]["node_object"].__dict__ == node.__dict__
        assert base_G.nodes["func_a"]["output"] == "o"
        assert base_G.nodes["func_a"]["signature"] == node.signature

    def test_set_node_objects_from(self, base_G):
        """Test set_node_objects_from method.

        Test if the edge attributes are updated.
        """

        def func_b(o, p):
            return o + p

        def func_c(o, s):
            return o + s

        base_G.set_node_objects_from(
            [Node("func_b", func_b, output=["q"]), Node("func_c", func_c, output=["t"])]
        )

        assert base_G.edges["func_a", "func_b"] == {"var": "o"}
        assert base_G.edges["func_a", "func_c"] == {"var": "o"}

    def test_node_metadata(self, mmodel_G):
        """Test node metadata.

        The doc parsing is also tested in metadata and node modules.
        """

        node = mmodel_G.nodes["add"]["node_object"]
        assert node.doc == "Add a constant to the value a."

        node = mmodel_G.nodes["log"]["node_object"]
        assert node.doc == "Logarithm operation."

        node = mmodel_G.nodes["power"]["node_object"]
        assert node.doc == "Return x**y (x to the power of y)."

        node = mmodel_G.nodes["subtract"]["node_object"]
        assert node.doc == "Same as a - b."


class TestGraphBasics:
    """Test the basic string and repr of the graph and nodes."""

    def test_networkx_equality(self, mmodel_G, standard_G):
        """Test if Graph instance matches ``networkx.DiGraph``."""

        assert graph_equal(mmodel_G, standard_G)

    def test_graph_name(self, mmodel_G):
        """Test naming and docs of the graph."""

        assert mmodel_G.name == "test_graph"

    def test_graph_str(self, mmodel_G):
        """Test graph representation."""

        assert str(mmodel_G) == "Graph named 'test_graph' with 5 nodes and 5 edges"

    def test_visualize(self, mmodel_G):
        """Test the visualize method of Graph instance.

        The draw methods are tested in the visualizer module.
        Here we make sure the label is correct.
        """

        dot_graph = mmodel_G.visualize()
        label = """label="Graph named \'test_graph\' with 5 nodes and 5 edges"""
        assert label in dot_graph.source

    def test_visualize_export(self, mmodel_G, tmp_path):
        """Test the visualize method that exports to files.

        Check the graph description in the file content.
        """

        filename = tmp_path / "test_draw.dot"
        mmodel_G.visualize(outfile=filename)

        label = """label="Graph named \'test_graph\' with 5 nodes and 5 edges"""

        with open(filename, "r") as f:
            assert label in f.read()

    def test_str_representation(self, mmodel_G):
        """Test if view node outputs node information correctly."""

        node_s = """\
        log

        logarithm(c, b)
        return: m
        functype: function

        Logarithm operation."""

        assert str(mmodel_G.nodes["log"]["node_object"]) == dedent(node_s)


class TestNetworkXGraphOperation:
    """Test the copy, deepcopy, chain, subgraph, subgraph copy based on networkx."""

    def test_copy(self, mmodel_G):
        """Test if copy works with Graph."""

        assert graph_equal(mmodel_G.copy(), mmodel_G)
        assert mmodel_G.copy().graph is not mmodel_G.graph

    def test_deepcopy(self, mmodel_G):
        """Test if copy creates a new graph attribute dictionary."""

        G_deepcopy = mmodel_G.deepcopy()

        # check if the graph is correctly duplicated
        assert graph_equal(G_deepcopy, mmodel_G)
        # see test_copy that the two dictionaries are the same
        assert G_deepcopy.graph is not mmodel_G.graph
        # object being deepcopied
        assert G_deepcopy.nodes != mmodel_G.nodes

    def test_graph_chain(self, mmodel_G):
        """Test Chain graph."""

        G = mmodel_G
        DG = G.to_directed(as_view=True)
        SDG = DG.subgraph(["subtract", "power"])
        RSDG = SDG.reverse(copy=False)
        assert G is DG._graph
        assert DG is SDG._graph
        assert SDG is RSDG._graph

    def test_subgraph(self, mmodel_G):
        """Test subgraph.

        The networkx graph creates the subgraph as a view of the original graph.
        The Graph subgraph is a copy of the original graph.
        The copied graph no longer has the _graph attribute.
        """
        G = mmodel_G

        # full subgraph
        H = G.subgraph(["add", "multiply", "subtract", "power", "log"])
        assert graph_equal(H, G)  # check if they are the same

        # partial subgraph
        H = G.subgraph(["subtract"])
        assert H.adj == {"subtract": {}}

        # partial subgraph
        H = G.subgraph(["subtract", "multiply"])
        assert H.adj == {"subtract": {"multiply": {"var": "e"}}, "multiply": {}}

        # empty subgraph
        H = G.subgraph([])
        assert H.adj == {}
        assert G.adj != {}

    def test_subgraph_deepcopy(self, mmodel_G):
        """Test the subgraph is copied.

        The subgraph no longer shares the graph attribute dictionary
        with the original graph.

        The subgraph view retains the graph attribute, and the copy method is only a
        shallow copy. Modify a copied subgraph attribute changes the original graph.
        """

        H = mmodel_G.subgraph(["subtract", "multiply"]).deepcopy()

        assert H.adj == {"subtract": {"multiply": {"var": "e"}}, "multiply": {}}

        # check the graph attribute is no longer the same dictionary`
        assert H.graph is not mmodel_G.graph

        H.name = "subgraph_test"
        assert mmodel_G.name != "subgraph_test"


class TestMGraphOperation:
    """Test graph operation defined specific to mmodel."""

    def test_subgraph_by_outputs(self, mmodel_G):
        """Test subgraph if outputs are specified."""

        subgraph = mmodel_G.subgraph(outputs=["m"])
        assert graph_equal(subgraph, mmodel_G.subgraph(nodes=["add", "log"]))

    def test_subgraph_by_inputs(self, mmodel_G):
        """Test subgraph if inputs are specified."""

        subgraph = mmodel_G.subgraph(inputs=["f"])
        assert graph_equal(subgraph, mmodel_G.subgraph(nodes=["power", "multiply"]))

    def test_subgraph_combined(self, mmodel_G):
        """Test subgraph with nodes, outputs, and inputs.

        The resulting graph should be the union of all selected values.
        """

        subgraph = mmodel_G.subgraph(inputs=["f"], outputs=["m"])
        assert graph_equal(
            subgraph, mmodel_G.subgraph(nodes=["add", "log", "power", "multiply"])
        )

        subgraph = mmodel_G.subgraph(nodes=["subtract"], inputs=["f"], outputs=["m"])
        assert graph_equal(subgraph, mmodel_G)

    def test_replace_subgraph(self, mmodel_G, value_modifier):
        """Test the replace_subgraph method replace the graph.

        See utils.replace_subgraph for more tests.
        """

        subgraph = mmodel_G.subgraph(["multiply", "power"])

        def func(a, b, c, d):
            return a + b + c + d

        node_object = Node(
            "test",
            func,
            output="z",
            inputs=["c", "e", "x", "y"],
            modifiers=[value_modifier(value=1)],
        )
        graph = mmodel_G.replace_subgraph(subgraph, node_object)

        # a copy is created
        assert graph != mmodel_G
        assert "test" in graph

        node_dict = graph.nodes["test"]
        assert list(node_dict["signature"].parameters) == ["c", "e", "x", "y"]
        assert node_dict["output"] == "z"

        assert node_dict["node_object"] == node_object
        # Test the edge attributes
        assert graph.edges["add", "test"]["var"] == "c"
        assert graph.edges["subtract", "test"]["var"] == "e"

    def test_get_node(self, mmodel_G):
        """Test get_node method."""

        node = mmodel_G.get_node("add")
        assert node == mmodel_G.nodes["add"]

    def test_get_node_obj(self, mmodel_G):
        """Test get_node_obj method."""

        node_object = mmodel_G.get_node_obj("add")
        assert node_object == mmodel_G.nodes["add"]["node_object"]

    def test_edit_node(self, mmodel_G, value_modifier):
        """Test edit_node method."""

        old_obj = mmodel_G.nodes["subtract"]["node_object"]

        G = mmodel_G.edit_node("subtract", modifiers=[value_modifier(value=2)])
        new_obj = G.nodes["subtract"]["node_object"]
        # add one to the final value
        assert new_obj(1, 2) == 1
        assert new_obj != old_obj

    def test_edit_node_new_signature(self, mmodel_G, value_modifier):
        """Test edit_node method."""

        old_obj = mmodel_G.nodes["add"]["node_object"]

        def add(first, second):
            return first + second

        # need to change inputs as well
        G = mmodel_G.edit_node(
            "add", func=add, modifiers=[value_modifier(value=2)], inputs=None
        )
        new_obj = G.nodes["add"]["node_object"]
        # add one to the final value
        assert list(new_obj.signature.parameters.keys()) == ["first", "second"]
        assert list(modelgraph_signature(G).parameters.keys()) == [
            "b",
            "d",
            "f",
            "first",
            "second",
        ]
        assert new_obj(first=1, second=2) == 5
        assert new_obj != old_obj
