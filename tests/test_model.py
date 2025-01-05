import inspect
import pytest
import math
import networkx as nx
from copy import deepcopy
from textwrap import dedent
import re
from mmodel import Model, BasicHandler, H5Handler, MemHandler, Graph, Node
from mmodel.modifier import loop_input


class TestModel:
    """Test Model instances."""

    def test_model_attr(self, model_instance, mmodel_signature):
        """Test the model has the correct name, signature, returns."""

        assert model_instance.name == "model_instance"
        assert model_instance.__name__ == "model_instance"
        assert model_instance.__signature__ == mmodel_signature
        assert model_instance.signature == mmodel_signature
        assert model_instance.returns == ["k", "m"]
        assert model_instance.modifiers == []
        assert model_instance.order == ("add", "subtract", "power", "log", "multiply")
        # doc works for inspect.getdoc and help()
        assert inspect.getdoc(model_instance) == model_instance.doc
        assert repr(model_instance) == "<mmodel.model.Model 'model_instance'>"

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

    def test_model_execution_binding(self, model_instance):
        """Test if the model execution checks the argument binding."""

        with pytest.raises(
            TypeError,
            match="missing a required argument: 'f'",
        ):
            model_instance(10, 2, 15)

        with pytest.raises(
            TypeError,
            match="too many positional arguments",
        ):
            model_instance(10, 2, 15, 1, 13)

        with pytest.raises(
            TypeError,
            match="got an unexpected keyword argument 'g'",
        ):
            model_instance(10, 2, 15, 1, g=13)

    def test_metadata_without_no_return(self):
        """Test metadata that doesn't have a return.

        The function has an output and execution should ignore the output.
        """
        G = Graph()
        G.add_node("Test")
        G.set_node_object(Node("Test", lambda x: x))
        model = Model("test_model", G, BasicHandler, doc="Test model.")

        assert model(1) == None  # test if the return is None

    def test_model_with_no_inputs(self):
        """Test model with no inputs."""

        G = Graph()
        G.add_node("Test")
        G.set_node_object(Node("Test", lambda: 1, output="value"))
        model = Model("test_model", G, BasicHandler, doc="Test model.")

        assert model() == 1

    def test_get_node(self, model_instance, mmodel_G):
        """Test get_node method of the model."""
        node_attr = model_instance.get_node("log")

        assert (
            node_attr.pop("node_object").__dict__
            == mmodel_G.nodes["log"].pop("node_object").__dict__
        )

        assert node_attr == mmodel_G.nodes["log"]

    def test_get_node_obj(self, model_instance, mmodel_G):
        """Test get_node_object method of the model."""

        assert (
            model_instance.get_node_object("log").__dict__
            == mmodel_G.nodes["log"]["node_object"].__dict__
        )

    def test_model_visualize(self, model_instance):
        """Test if the draw method of the model_instance.

        The draw methods are tested in visualizer module. Here we make sure
        the label is correct.
        """
        dot_graph = model_instance.visualize()

        assert str(model_instance).replace("\n", r"\l") in dot_graph.source

    def test_model_draw_export(self, model_instance, tmp_path):
        """Test the draw method that exports to files.

        Check the model description is in the file content.
        """

        filename = tmp_path / "test_draw.dot"
        model_instance.visualize(outfile=filename)
        reference = str(model_instance).replace("\n", "").replace(r"\l", "")

        with open(filename, "r") as f:
            assert reference in f.read().replace("\n", "").replace(r"\l", "").replace(
                "\\", ""
            )

    def test_model_with_handler_argument(self, mmodel_G, tmp_path):
        """Test if the argument works with the H5Handler."""

        path = tmp_path / "h5model_test.h5"
        h5model = Model("h5 model", mmodel_G, H5Handler, handler_kwargs={"fname": path})

        assert h5model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2))

        # the output of the path is the repr instead of the string
        assert "handler: H5Handler" in str(h5model)
        assert "handler_kwargs" in str(h5model)
        assert re.search(r"- fname: .*? \[\.\.\.\]", str(h5model))

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

    def test_model_edit(self, mmodel_G):
        """Test model editing.

        The function should return a new model instance.
        """

        model = Model(
            "model_instance",
            mmodel_G,
            BasicHandler,
            param_defaults={"a": 10, "b": 2},
            doc="Old doc",
            add_args="additional arguments",
        )

        new_model = model.edit(
            name="new_model", handler=MemHandler, doc="Model description."
        )
        assert new_model.name == "new_model"
        assert new_model.doc == "Model description."
        assert new_model.__doc__ == "Model description."
        assert new_model.handler == MemHandler
        assert model.graph is not new_model.graph
        assert model.param_defaults == new_model.param_defaults
        assert new_model.add_args == "additional arguments"
        assert new_model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2))

    def test_model_defaults(self, mmodel_G):
        """Test model with default values."""

        model = Model(
            "model_instance",
            mmodel_G,
            BasicHandler,
            param_defaults={"a": 10, "b": 2},
        )
        assert list(model.signature.parameters.keys()) == ["d", "f", "a", "b"]
        assert model(d=15, f=1) == (-36, math.log(12, 2))


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
            doc="Modified model.",
            add_args="additional arguments",
        )

    def test_mod_model_attr(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)."""

        assert mod_model_instance.returns == ["k", "m"]

    def test_mod_model_execution(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)."""

        assert mod_model_instance(a_loop=[1, 2], b=2, d=3, f=1) == [
            (0, math.log(3, 2)),
            (4, 2),
        ]

    def test_model_str(self, mod_model_instance):
        """Test the string representation with modifiers."""
        mod_model_s = """\
        mod_model_instance(a_loop, b, d, f)
        returns: (k, m)
        graph: test_graph
        handler: BasicHandler
        modifiers:
        - loop_input(parameter='a')
        
        Modified model."""
        assert str(mod_model_instance) == dedent(mod_model_s)

    def test_model_edit_node(self, mod_model_instance):
        """Test if the edit method works with node."""

        new_model = mod_model_instance.edit_node("log", func=math.log2, inputs=["c"])

        assert new_model is not mod_model_instance

        assert list(new_model.signature.parameters.keys()) == ["a_loop", "d", "f"]
        assert new_model.add_args == "additional arguments"
        assert new_model.returns == ["k", "m"]
        assert new_model(a_loop=[1, 2], d=15, f=1) == [(-36, math.log2(3)), (-44, 2)]

    def test_model_edit_node_exception(self, mod_model_instance):
        """Test if the edit method resets edge attribute if incorrect."""

        with pytest.raises(
            Exception,
            match=r"invalid graph \(test_graph\): attribute 'output' "
            r"is not defined for edge\(s\) \[\('power', 'multiply'\)\].",
        ):
            mod_model_instance.edit_node("power", output="incorrect_output")


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
                r"invalid graph \(test_graph\): attribute 'node_object' "
                r"is not defined for node\(s\) \['test'\]."
            ),
        ):
            Model._is_valid_graph(G)

        # manual adding the object
        G.nodes["test"]["node_object"] = Node(
            "test", test, output="c", inputs=["a", "b"]
        )

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): attribute 'output' "
                r"is not defined for node\(s\) \['test'\]"
            ),
        ):
            Model._is_valid_graph(G)

        G.nodes["test"]["output"] = "c"

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): attribute 'signature' "
                r"is not defined for node\(s\) \['test'\]"
            ),
        ):
            Model._is_valid_graph(G)

        G.nodes["test"]["signature"] = inspect.signature(test)

        with pytest.raises(
            Exception,
            match=(
                r"invalid graph \(test_graph\): attribute 'output' "
                r"is not defined for edge\(s\) \[\('log', 'test'\)\]"
            ),
        ):
            Model._is_valid_graph(G)

        # the last one will pass even tho it is empty

        G.edges["log", "test"]["output"] = "t"
        assert Model._is_valid_graph(G)

    def test_is_valid_graph_passing(self, mmodel_G):
        """Test is_valid_graph that correctly passing."""

        assert Model._is_valid_graph(mmodel_G)
