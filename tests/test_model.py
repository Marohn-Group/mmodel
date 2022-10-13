import inspect
import pytest
from mmodel.model import Model
from mmodel.handler import BasicHandler, H5Handler
from mmodel.modifier import loop_modifier
import math
import networkx as nx
from copy import deepcopy
from textwrap import dedent
from tests.conftest import graph_equal


class TestModel:
    """Test Model instances"""

    @pytest.fixture
    def model_instance(self, mmodel_G):
        """Construct a model_instance"""

        return Model(
            "model_instance", mmodel_G, (BasicHandler, {}), description="example model"
        )

    def test_model_attr(self, model_instance, mmodel_signature):
        """Test the model has the correct name, signature, returns"""

        assert model_instance.__name__ == "model_instance"
        assert model_instance.__signature__ == mmodel_signature
        assert model_instance.returns == ["k", "m"]
        assert model_instance.modifiers == []

    def test_model_output(self, mmodel_G):
        return Model(
            "model_instance", mmodel_G, (BasicHandler, {}), description="example model"
        )

    def test_model_str(self, model_instance):
        """Test model representation"""

        MODEL_STR = """\
        model_instance(a, d, f, b=2)
          returns: k, m
          handler: BasicHandler, {}
          modifiers: []
        example model"""

        assert str(model_instance) == dedent(MODEL_STR)

    def test_model_graph_freeze(self, model_instance):
        """Test the graph is frozen"""

        assert nx.is_frozen(model_instance.graph)

    def test_model_execution(self, model_instance):
        """Test if the default is correctly used"""

        assert model_instance(10, 15, 1) == (-36, math.log(12, 2))
        assert model_instance(a=1, d=2, f=3, b=4) == (375, math.log(5, 4))

    def test_get_node(self, model_instance, mmodel_G):
        """Test get_node method of the model"""

        assert model_instance.get_node("log") == mmodel_G.nodes["log"]

    def test_get_node_object(self, model_instance, mmodel_G):
        """Test get_node_object method"""

        assert model_instance.get_node_object("log") == mmodel_G.nodes["log"]["func"]

    def test_model_draw(self, model_instance):
        """Test if the draw method of the model_instance

        The draw methods are tested in test_draw module. Here we make sure
        the label is correct.
        """
        dot_graph = model_instance.draw()

        assert str(model_instance).replace("\n", "\l") in dot_graph.source

    def test_model_view_node(self, model_instance):
        """Test if view node outputs node information correctly"""

        node_s = """\
        log
          callable: logarithm(c, b)
          return: m
          modifiers: []"""

        assert model_instance.view_node("log") == dedent(node_s)

    def test_model_with_handler_argument(self, mmodel_G, tmp_path):
        """Test if argument works with the H5Handler"""

        path = tmp_path / "h5model_test.h5"
        h5model = Model("h5 model", mmodel_G, (H5Handler, {"fname": path}))

        assert h5model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2))

        # the output of path is the repr instead of string
        assert f"handler: H5Handler, {{'fname': {repr(path)}}}" in str(h5model)

    def test_model_returns_same(self, mmodel_G):
        """Test model with custom returns

        The return order should be the same as the returns list, and the base graph
        and graph should be the same (same object in fact)
        """

        # less returns
        model = Model(
            "model_instance", mmodel_G, (BasicHandler, {}), returns=["m", "k"]
        )
        assert model.graph is model.base_graph
        assert model.returns == ["m", "k"]
        assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36)

    def test_model_returns_more(self, mmodel_G):
        """Test model with custom returns that are more than graph"""
        # more returns
        model = Model(
            "model_instance", mmodel_G, (BasicHandler, {}), returns=["m", "k", "c"]
        )
        assert model.graph is model.base_graph
        assert model.returns == ["m", "k", "c"]
        assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36, 12)

    def test_model_returns_less(self, mmodel_G):
        """Test model with custom returns that are less than graph
        
        In this case the graph is adjusted
        """
        # more returns
        model = Model(
            "model_instance", mmodel_G, (BasicHandler, {}), returns=["k"]
        )

        assert graph_equal(model.base_graph, mmodel_G)
        assert 'log' not in model.graph.nodes
        assert nx.is_frozen(model.graph) # check that it is frozen
        assert model.returns == ["k"]
        assert model(a=10, d=15, f=1, b=2) == -36

    def test_model_returns_less_partial(self, mmodel_G):
        """Test model with less than graph returns but with added intermediate value
        
        In this case the graph is adjusted
        """
        # more returns
        model = Model(
            "model_instance", mmodel_G, (BasicHandler, {}), returns=["k", "c"]
        )

        assert graph_equal(model.base_graph, mmodel_G)
        assert 'log' not in model.graph.nodes
        assert nx.is_frozen(model.graph) # check that it is frozen
        assert model.returns == ["k", "c"]
        assert model(a=10, d=15, f=1, b=2) == (-36, 12)


class TestModifiedModel:
    """Test modified model"""

    @pytest.fixture
    def mod_model_instance(self, mmodel_G):
        """Construct a model_instance with loop modifier"""

        loop_mod = (loop_modifier, {"parameter": "a"})

        return Model(
            "mod_model_instance",
            mmodel_G,
            (BasicHandler, {}),
            modifiers=[loop_mod],
            description="modified model",
        )

    def test_mod_model_attr(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)"""

        assert mod_model_instance.returns == ["k", "m"]

    def test_mod_model_execution(self, mod_model_instance):
        """Test if adding modifier changes the handler attribute (returns)"""

        assert mod_model_instance(a=[1, 2], b=2, d=3, f=1) == [
            (0, math.log(3, 2)),
            (4, 2),
        ]

    def test_model_str(self, mod_model_instance):
        """Test the string representation with modifiers"""
        mod_model_s = """\
        mod_model_instance(a, d, f, b=2)
          returns: k, m
          handler: BasicHandler, {}
          modifiers: [loop_modifier, {'parameter': 'a'}]
        modified model"""
        assert str(mod_model_instance) == dedent(mod_model_s)


class TestModelValidation:
    """Test is_graph_valid method of Model"""

    def test_is_valid_graph_digraph(self):
        """Test is_graph_valid that correctly identifies non directed graphs"""

        g = nx.complete_graph(4)

        with pytest.raises(AssertionError, match="invalid graph: undirected graph"):
            Model._is_valid_graph(g)

    def test_is_valid_graph_cycles(self):
        """Test is_graph_valid that correctly identifies cycles

        Check a self cycle and a non self cycle
        """

        g = nx.DiGraph()
        g.add_edges_from([[1, 2], [2, 3], [3, 1]])
        # cycle goes from 1 -> 2 -> 3 -> 1

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains cycles"
        ):
            Model._is_valid_graph(g)

        g = nx.DiGraph()
        g.add_edge(1, 1)
        # cycle goes from 1 -> 1

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains cycles"
        ):
            Model._is_valid_graph(g)

    def test_is_valid_graph_isolates(self):
        """Test is_graph_valid that correctly identifies isolated nodes"""

        g = nx.DiGraph()
        g.add_edges_from([[1, 2], [2, 3]])
        g.add_node(4)
        # 4 is the isolated node

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains isolated nodes"
        ):
            Model._is_valid_graph(g)

    def test_is_valid_graph_missing_attr(self, standard_G):
        """Test is_graph_valid that correctly identifies isolated nodes

        Here we add nodes to mmodel_G
        """

        def test(a, b):
            return

        g = deepcopy(standard_G)
        g.add_edge("log", "test")

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains nodes with undefined callables",
        ):
            Model._is_valid_graph(g)

        g.nodes["test"]["func"] = test

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains nodes with undefined callables output",
        ):
            Model._is_valid_graph(g)

        g.nodes["test"]["output"] = "c"

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains nodes with undefined callables signatures",
        ):
            Model._is_valid_graph(g)

        g.nodes["test"]["sig"] = inspect.signature(test)

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains edges with undefined variable attributes",
        ):
            Model._is_valid_graph(g)

        # the last one will pass even tho it is empty

        g.edges["log", "test"]["val"] = None
        assert Model._is_valid_graph(g)

    def test_is_valid_graph_passing(self, mmodel_G):
        """Test is_valid_graph that correctly passing"""

        assert Model._is_valid_graph(mmodel_G)
