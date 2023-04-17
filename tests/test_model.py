import inspect
import pytest
import math
import networkx as nx
from copy import deepcopy
from textwrap import dedent
import numpy as np

from mmodel import Model, BasicHandler, H5Handler, MemHandler, ModelGraph
from mmodel.modifier import loop_input


class TestModel:
    """Test Model instances."""

    @pytest.fixture
    def model_instance(self, mmodel_G):
        """Construct a model_instance."""
        description = (
            "A long description that tests if the model module"
            " wraps the Model output string description at 90 characters."
        )
        return Model("model_instance", mmodel_G, BasicHandler, description=description)

    def test_model_attr(self, model_instance, mmodel_signature):
        """Test the model has the correct name, signature, returns."""

        assert model_instance.name == "model_instance"
        assert model_instance.__name__ == "model_instance"
        assert model_instance.__signature__ == mmodel_signature
        assert model_instance.returns == ["k", "m"]
        assert model_instance.modifiers == []
        assert model_instance.execution_order == [
            "add",
            "subtract",
            "power",
            "log",
            "multiply",
        ]

    def test_model_str(self, model_instance):
        """Test model representation."""

        model_str = """\
        model_instance(a, b, d, f)
        returns: (k, m)
        graph: test_graph
        handler: BasicHandler

        A long description that tests if the model module wraps the Model output string
          description at 90 characters."""

        assert str(model_instance) == dedent(model_str)

    def test_model_graph_freeze(self, model_instance):
        """Test the graph is frozen."""

        assert nx.is_frozen(model_instance._graph)

    def test_model_original_graph_not_frozen(self, mmodel_G):
        """Make sure that the original graph is not frozen when defining models."""

        Model("model_instance", mmodel_G, BasicHandler)
        assert not nx.is_frozen(mmodel_G)

    def test_model_graph_property(self, model_instance):
        """Test the graph attribute generates a copy of the graph every time."""

        assert not nx.is_frozen(model_instance.graph)
        assert model_instance.graph is not model_instance._graph

    def test_model_execution(self, model_instance):
        """Test if the default is correctly used."""

        assert model_instance(10, 2, 15, 1) == (-36, math.log(12, 2))
        assert model_instance(a=1, d=2, f=3, b=4) == (27, math.log(3, 4))

    def test_metadata_without_no_return(self):
        """Test metadata that doesn't have a return.

        The function has an output and execution should ignore the output.
        """
        G = ModelGraph()
        G.add_node("Test")
        G.set_node_object("Test", lambda x: x, output=None)
        model = Model("test_model", G, BasicHandler, description="Test model.")

        assert model(1) == None  # test if the return is None

    def test_get_node(self, model_instance, mmodel_G):
        """Test get_node method of the model."""

        assert model_instance.get_node("log") == mmodel_G.nodes["log"]

    def test_get_node_func(self, model_instance, mmodel_G):
        """Test get_node_func method."""

        assert model_instance.get_node_func("log") == mmodel_G.nodes["log"]["_func"]

    def test_model_draw(self, model_instance):
        """Test if the draw method of the model_instance.

        The draw methods are tested in test_draw module. Here we make sure
        the label is correct.
        """
        dot_graph = model_instance.draw()

        assert str(model_instance).replace("\n", "\l") in dot_graph.source

    def test_model_draw_export(self, model_instance, tmp_path):
        """Test the draw method that exports to files.

        Check the model description is in the file content.
        """

        filename = tmp_path / "test_draw.dot"
        model_instance.draw(export=filename)
        reference = str(model_instance).replace("\n", "").replace("\l", "")

        with open(filename, "r") as f:

            assert reference in f.read().replace("\n", "").replace("\l", "").replace(
                "\\", ""
            )

    def test_model_node_metadata(self, model_instance):
        """Test if view node outputs information correctly."""

        node_s = """\
        log

        logarithm(c, b)
        return: m
        functype: callable

        Logarithm operation."""

        assert model_instance.node_metadata("log") == dedent(node_s)

    def test_model_with_handler_argument(self, mmodel_G, tmp_path):
        """Test if the argument works with the H5Handler."""

        path = tmp_path / "h5model_test.h5"
        h5model = Model("h5 model", mmodel_G, H5Handler, fname=path)

        assert h5model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2))

        # the output of the path is the repr instead of the string
        assert f"handler: H5Handler" in str(h5model)
        assert f"handler args" in str(h5model)
        assert f"- fname: {path}" in str(h5model).replace("\n  ", "")

    def test_model_returns_order(self, mmodel_G):
        """Test model with custom returns order.

        The return order should be the same as the returns list.
        """

        model = Model("model_instance", mmodel_G, BasicHandler, returns=["m", "k"])

        assert model.returns == ["m", "k"]
        assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36)

    def test_model_returns_intermediate(self, mmodel_G):
        """Test model with custom returns that are more than graph."""
        # more returns
        model = Model("model_instance", mmodel_G, BasicHandler, returns=["m", "k", "c"])

        assert model.returns == ["m", "k", "c"]
        assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36, 12)

    def test_model_edit(self, model_instance):
        """Test model editing.

        The function should return a new model instance.
        """

        new_model = model_instance.edit(
            name="new_model", handler=MemHandler, description="Model description."
        )
        assert new_model.name == "new_model"
        assert new_model.description == "Model description."
        assert new_model.handler == MemHandler
        assert model_instance.graph is not new_model.graph

        assert new_model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2))


class TestModelMetaData:
    """Test the model instance metadata."""

    @pytest.fixture
    def func(self):
        """A test function."""

        def _func(a, b):
            return a + b

        return _func

    @pytest.fixture
    def G(self):
        """An graph with one node."""

        G = ModelGraph(name="meta test graph")
        G.add_node("Test")
        return G

    def test_metadata_dict(self, func, G):
        """Test metadata_dict that has all key and value pairs.

        Test both the verbose and non-verbose versions.
        """
        G.set_node_object("Test", func, output="c")
        model = Model("test_model", G, BasicHandler, description="Test model.")

        assert sorted(list(model._metadata_dict(True).keys())) == [
            "description",
            "graph",
            "handler",
            "handler args",
            "model",
            "modifiers",
            "returns",
        ]

        assert sorted(list(model._metadata_dict(False).keys())) == ["model", "returns"]


class TestModifiedModel:
    """Test modified model."""

    @pytest.fixture
    def mod_model_instance(self, mmodel_G):
        """Construct a model_instance with loop_input modifier."""

        return Model(
            "mod_model_instance",
            mmodel_G,
            BasicHandler,
            modifiers=[loop_input("a")],
            description="Modified model.",
        )

    def test_mod_model_attr(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)."""

        assert mod_model_instance.returns == ["k", "m"]

    def test_mod_model_execution(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)."""

        assert mod_model_instance(a=[1, 2], b=2, d=3, f=1) == [
            (0, math.log(3, 2)),
            (4, 2),
        ]

    def test_model_str(self, mod_model_instance):
        """Test the string representation with modifiers."""
        mod_model_s = """\
        mod_model_instance(a, b, d, f)
        returns: (k, m)
        graph: test_graph
        handler: BasicHandler
        modifiers:
          - loop_input('a')
        
        Modified model."""
        assert str(mod_model_instance) == dedent(mod_model_s)


class TestModelValidation:
    """Test is_graph_valid method of Model."""

    def test_is_valid_graph_digraph(self):
        """Test is_graph_valid that correctly identifies non-directed graphs."""

        G = nx.complete_graph(4)
        G.name = "test_graph"

        with pytest.raises(
            AssertionError, match=r"invalid graph \(test_graph\): undirected graph"
        ):
            Model._is_valid_graph(G)

    def test_is_valid_graph_cycles(self):
        """Test is_graph_valid that correctly identifies cycles.

        Check the self-cycle and the nonself cycle.
        """

        G = nx.DiGraph(name="test_graph")
        G.add_edges_from([[1, 2], [2, 3], [3, 1]])
        # cycle goes from 1 -> 2 -> 3 -> 1

        with pytest.raises(
            AssertionError, match=r"invalid graph \(test_graph\): graph contains cycles"
        ):
            Model._is_valid_graph(G)

        G = nx.DiGraph(name="test_graph")
        G.add_edge(1, 1)
        # cycle goes from 1 -> 1

        with pytest.raises(
            AssertionError, match=r"invalid graph \(test_graph\): graph contains cycles"
        ):
            Model._is_valid_graph(G)

    def test_is_valid_graph_missing_attr(self, standard_G):
        """Test is_graph_valid that correctly identifies isolated nodes.

        Here we add nodes to mmodel_G.
        """

        def test(a, b):
            return

        G = deepcopy(standard_G)
        G.add_edge("log", "test")
        # G.name = "test_graph"

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): callable 'func' "
                r"is not defined for node\(s\) \['test'\]"
            ),
        ):
            Model._is_valid_graph(G)

        G.nodes["test"]["func"] = test

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): output 'output' "
                r"is not defined for node\(s\) \['test'\]"
            ),
        ):
            Model._is_valid_graph(G)

        G.nodes["test"]["output"] = "c"

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): signature 'sig' "
                r"is not defined for node\(s\) \['test'\]"
            ),
        ):
            Model._is_valid_graph(G)

        G.nodes["test"]["sig"] = inspect.signature(test)

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): variable 'var' "
                r"is not defined for edge\(s\) \[\('log', 'test'\)\]"
            ),
        ):
            Model._is_valid_graph(G)

        # the last one will pass even tho it is empty

        G.edges["log", "test"]["var"] = None
        assert Model._is_valid_graph(G)

    def test_is_valid_graph_passing(self, mmodel_G):
        """Test is_valid_graph that correctly passing."""

        assert Model._is_valid_graph(mmodel_G)


class TestModelSpecialFunc:
    """Test models with builtin or numpy.ufunc."""

    @pytest.fixture
    def model(self):
        """Basic Model with builtin and ufunc nodes."""

        G = ModelGraph()
        G.add_edge("func_a", "func_b")

        G.set_node_object("func_a", np.add, "x", inputs=["a", "b"])
        G.set_node_object("func_b", math.ceil, "p", inputs=["x"])

        return Model(
            "model_instance",
            G,
            BasicHandler,
            description="Model with builtin and ufunc.",
        )

    def test_model_signature(self, model):
        """Test model signature."""

        assert list(inspect.signature(model).parameters.keys()) == ["a", "b"]

    def test_model_execution(self, model):
        """Test model result."""

        assert model(3, 1.9) == 5
