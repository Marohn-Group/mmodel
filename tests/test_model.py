import inspect
import pytest
from mmodel.model import Model
from mmodel.handler import BasicHandler, H5Handler
from mmodel.modifier import loop_modifier
import math
import networkx as nx
from copy import deepcopy


def test_invalid_model(mmodel_G):
    """Test if invalid model raises an assertion error of incorrect graph"""

    g = mmodel_G.deepcopy()
    # add a new node and edge
    g.add_edge("log", "test")

    with pytest.raises(AssertionError):
        Model("invalid graph model", g, (BasicHandler, {}))


def test_default_modifier(mmodel_G):
    """Test if default modifiers is changed to [] if input is None"""

    model = Model("test model", mmodel_G, (BasicHandler, {}))
    assert model.modifiers == []


MODEL_STR = """\
model_instance(a, d, f, b=2)
  returns: k, m, p
  handler: BasicHandler, {}
  modifiers: []
test model description"""


@pytest.fixture
def model_instance(mmodel_G):
    """Construct a model_instance"""
    description = "test model description"
    return Model("model_instance", mmodel_G, (BasicHandler, {}), [], description)


def test_model_attr(model_instance, mmodel_signature):
    """Test the model has the correct name, signature, returns"""

    assert model_instance.__name__ == "model_instance"
    assert model_instance.__signature__ == mmodel_signature
    assert model_instance.returns == ["k", "m", "p"]


def test_model_str(model_instance):
    """Test model representation"""

    assert str(model_instance) == MODEL_STR


def test_model_graph_freeze(model_instance):
    """Test the graph is frozen"""

    assert nx.is_frozen(model_instance.graph)


def test_model_execution(model_instance):
    """Test if the default is correctly used"""

    assert model_instance(10, 15, 1) == (-36, math.log(12, 2), 1)
    assert model_instance(a=1, d=2, f=3, b=4) == (375, math.log(5, 4), 243)


def test_get_node(model_instance, mmodel_G):
    """Test get_node method of the model"""

    assert model_instance.get_node("log") == mmodel_G.nodes["log"]


def test_get_node_object(model_instance, mmodel_G):
    """Test get_node_object method"""

    assert model_instance.get_node_object("log") == mmodel_G.nodes["log"]["func"]


def test_model_draw(model_instance):
    """Test if the draw method of the model_instance

    The draw methods are tested in test_draw module. Here we make sure
    the label is correct.
    """
    dot_graph = model_instance.draw()

    assert str(model_instance).replace("\n", "\l") in dot_graph.source


NODE_STR = """\
log node
  callable: logarithm(c, b)
  returns: m
  modifiers: []"""


def test_model_view_node(model_instance):
    """Test if view node outputs node information correctly"""

    assert model_instance.view_node("log") == NODE_STR


MOD_MODEL_STR = """\
model_instance(a, d, f, b=2)
  returns: k, m, p
  handler: BasicHandler, {}
  modifiers: [loop_modifier, {'parameter': 'a'}]
test model description"""


def test_mod_model_str(mmodel_G):
    """Test the string representation with modifiers

    with multiple modifiers, the modifiers are delimited by ", "
    """
    single_mod = Model(
        "model_instance",
        mmodel_G,
        (BasicHandler, {}),
        [(loop_modifier, {"parameter": "a"})],
        "test model description",
    )
    assert str(single_mod) == MOD_MODEL_STR

    double_mod = Model(
        "model_instance",
        mmodel_G,
        (BasicHandler, {}),
        modifiers=[
            (loop_modifier, {"parameter": "a"}),
            (loop_modifier, {"parameter": "b"}),
        ],
        description="description",
    )
    assert (
        "modifiers: [loop_modifier, {'parameter': 'a'}, loop_modifier, {'parameter': 'b'}]"
        in str(double_mod)
    )


@pytest.fixture
def mod_model_instance(mmodel_G):
    """Construct a model_instance with loop modifier"""

    loop_mod = (loop_modifier, {"parameter": "a"})

    return Model(
        "mod model_instance", mmodel_G, (BasicHandler, {}), modifiers=[loop_mod]
    )


def test_mod_model_attr(mod_model_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert mod_model_instance.returns == ["k", "m", "p"]


def test_mod_model_execution(mod_model_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert mod_model_instance(a=[1, 2], b=2, d=3, f=1) == [
        (0, math.log(3, 2), 1),
        (4, 2, 1),
    ]


def test_model_with_handler_argument(mmodel_G, tmp_path):
    """Test if argument works with the H5Handler"""

    path = tmp_path / "h5model_test.h5"
    h5model = Model("h5 model", mmodel_G, (H5Handler, {"fname": path}))

    assert h5model(a=10, d=15, f=1, b=2) == (-36, math.log(12, 2), 1)

    # the output of path is the repr instead of string
    assert f"handler: H5Handler, {{'fname': {repr(path)}}}" in str(h5model)


def test_model_returns(mmodel_G):
    """Test model with custom returns

    The return order should be the same as the returns list
    """

    # less returns
    model = Model("model_instance", mmodel_G, (BasicHandler, {}), returns=["m", "k"])
    assert model.returns == ["m", "k"]
    assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36)

    # more returns
    model = Model(
        "model_instance", mmodel_G, (BasicHandler, {}), returns=["m", "k", "c"]
    )
    assert model.returns == ["m", "k", "c"]
    assert model(a=10, d=15, f=1, b=2) == (math.log(12, 2), -36, 12)


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
            match="invalid graph: graph contains nodes with undefined callables returns",
        ):
            Model._is_valid_graph(g)

        g.nodes["test"]["returns"] = ["c"]

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

        g.edges["log", "test"]["val"] = []
        assert Model._is_valid_graph(g)

    def test_is_valid_graph_passing(self, mmodel_G):
        """Test is_valid_graph that correctly passing"""

        assert Model._is_valid_graph(mmodel_G)
