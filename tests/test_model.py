import inspect
import pytest
from mmodel.model import Model
from mmodel.handler import PlainHandler, H5Handler
from mmodel.modifier import loop_modifier
import math
import networkx as nx


def test_invalid_model(mmodel_G):
    """Test if invalid model will raise an assertion error"""

    g = mmodel_G.copy()
    g.add_edge("log", "test")

    with pytest.raises(AssertionError):
        Model(g, PlainHandler)


MODEL_REPR = """test model
signature - a, d, f, b=2
returns - k, m
handler - PlainHandler
test object

long description"""


@pytest.fixture
def model_instance(mmodel_G):
    """Construct a model instance"""

    return Model(mmodel_G, PlainHandler)


def test_model_attr(model_instance, mmodel_signature):
    """Test the model has the correct name, signature, returns"""

    assert model_instance.__name__ == "test model"
    assert model_instance.__signature__ == mmodel_signature
    assert model_instance.returns == ["k", "m"]


def test_model_str(model_instance):
    """Test model representation"""

    assert str(model_instance) == MODEL_REPR


def test_execution(model_instance):
    """Test if the default is correctly used"""

    assert model_instance(10, 15, 20) == (-720, math.log(12, 2))
    assert model_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))


@pytest.fixture
def model_mod_instance(mmodel_G):
    """Construct a model instance"""

    loop_mod = loop_modifier("a")

    return Model(mmodel_G, PlainHandler, modifiers=[loop_mod])


def test_mod_attr(model_mod_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert model_mod_instance.returns == ["k", "m"]


def test_mod_execution(model_mod_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert model_mod_instance(a=[1, 2], b=2, d=3, f=4) == [(0, math.log(3, 2)), (16, 2)]


def test_mod_with_argument(mmodel_G):
    """Test if the handler arguments is correctly transferred"""

    h5model = Model(mmodel_G, H5Handler, handler_args={"h5_filename": "test_file"})

    assert h5model.executor.h5_filename == "test_file"


class TestModelValidation:
    """Test is_graph_valid method of Model"""

    def test_is_graph_valid_digraph(self):
        """Test is_graph_valid that correctly identifies non directed graphs"""

        g = nx.complete_graph(4)

        with pytest.raises(AssertionError, match="invalid graph: undirected graph"):
            Model.is_graph_valid(g)

    def test_is_graph_valid_cycles(self):
        """Test is_graph_valid that correctly identifies cycles

        Check a self cycle and a non self cycle
        """

        g = nx.DiGraph()
        g.add_edges_from([[1, 2], [2, 3], [3, 1]])
        # cycle goes from 1 -> 2 -> 3 -> 1

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains cycles"
        ):
            Model.is_graph_valid(g)

        g = nx.DiGraph()
        g.add_edge(1, 1)
        # cycle goes from 1 -> 1

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains cycles"
        ):
            Model.is_graph_valid(g)

    def test_is_graph_valid_isolates(self):
        """Test is_graph_valid that correctly identifies isolated nodes"""

        g = nx.DiGraph()
        g.add_edges_from([[1, 2], [2, 3]])
        g.add_node(4)
        # 4 is the isolated node

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains isolated nodes"
        ):
            Model.is_graph_valid(g)

    def test_is_graph_valid_missing_attr(self, standard_G):
        """Test is_graph_valid that correctly identifies isolated nodes

        Here we add nodes to mmodel_G
        """

        def test(a, b):
            return

        g = standard_G.copy()
        g.add_edge("log", "test")

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains nodes with undefined callables"
        ):
            Model.is_graph_valid(g)

        g.nodes["test"]["obj"] = test

        with pytest.raises(
            AssertionError, match="invalid graph: graph contains nodes with undefined callables returns"
        ):
            Model.is_graph_valid(g)

        g.nodes["test"]["returns"] = ["c"]

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains nodes with undefined callables signatures",
        ):
            Model.is_graph_valid(g)

        g.nodes["test"]["sig"] = inspect.signature(test)

        with pytest.raises(
            AssertionError,
            match="invalid graph: graph contains edges with undefined variable attributes"
        ):
            Model.is_graph_valid(g)

        # the last one will pass even tho it is empty

        g.edges["log", "test"]['val'] = []
        assert Model.is_graph_valid(g)

    def test_is_graph_valid_passing(self, mmodel_G):
        """Test is_graph_valid that correctly passing"""

        assert Model.is_graph_valid(mmodel_G)
