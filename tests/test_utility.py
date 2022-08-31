import inspect
import pytest
import random
import mmodel.utility as util
from collections import OrderedDict
from inspect import Parameter
from tests.conftest import graph_equal
import networkx as nx
from functools import wraps


def mock_func(a, c, b=2, *args, d, e=10, **kwargs):
    return


@pytest.mark.parametrize(
    "parameter, result",
    [
        ("a", (1, False, "a")),
        ("b", (1, True, "b")),
        ("args", (2, False, "args")),
        ("c", (1, False, "c")),
        ("d", (3, False, "d")),
        ("e", (3, True, "e")),
        ("kwargs", (4, False, "kwargs")),
    ],
)
def test_param_sorter(parameter, result):
    """Test param_sorter result"""

    params = inspect.signature(mock_func).parameters
    assert util.param_sorter(params[parameter]) == result


def test_param_sorter_order():
    """Test param_sorter sorting order

    the correct order is a, b, *args, c, **kwargs, d=10
    """

    params = inspect.signature(mock_func).parameters
    shuffled_params_list = list(params.items())
    random.shuffle(shuffled_params_list)
    shuffled_params = OrderedDict(shuffled_params_list)

    param_list = [
        Parameter("a", 1),
        Parameter("c", 1),
        Parameter("b", 1, default=2),
        Parameter("args", 2),
        Parameter("d", 3),
        Parameter("e", 3, default=10),
        Parameter("kwargs", 4),
    ]

    # inspect.Signature(param_list)
    assert sorted(shuffled_params.values(), key=util.param_sorter) == param_list


def test_model_signature(mmodel_G, mmodel_signature):
    """Test graph_signature

    There are two functions in the mmodel_G have parameter
    'b' - one with default and one without. The final signature
    should have default value.
    """

    assert util.model_signature(mmodel_G) == mmodel_signature


def test_replace_signature(mmodel_signature):
    """Test replace signature"""

    replacement_dict = {"a_rep": ["a"], "f_rep": ["f"]}
    signature = util.replace_signature(mmodel_signature, replacement_dict)

    assert "a_rep" in signature.parameters
    assert "a" not in signature.parameters
    assert "f_rep" in signature.parameters
    assert "f" not in signature.parameters

    # make sure the original signature is not modified
    assert "a_rep" not in mmodel_signature.parameters


def test_model_returns(mmodel_G):
    """Test graph_returns"""

    assert util.model_returns(mmodel_G) == ["k", "m"]


def test_graph_topological_sort(mmodel_G):
    """Test graph_topological_sort

    The order should be
    add, subtract, multiply, log, poly

    each node should be (node, attr), where node is the name
    of the node, attr is a dictionary of attributes
    """

    order = util.graph_topological_sort(mmodel_G)

    nodes = []

    for node, attr in order:
        assert isinstance(attr, dict)
        assert sorted(list(attr)) == ["base_obj", "func", "modifiers", "returns", "sig"]
        nodes.append(node)

    assert nodes == ["add", "subtract", "multiply", "log", "poly"]


def test_param_counter(mmodel_G):
    """Test param_counter"""

    counter = util.param_counter(mmodel_G, [])

    assert counter == {"a": 1, "b": 2, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1}


def test_param_counter_add_returns(mmodel_G):
    """Test param_counter with added returns"""

    counter = util.param_counter(mmodel_G, ["c", "g"])

    assert counter == {"a": 1, "b": 2, "c": 4, "d": 1, "e": 1, "f": 1, "g": 2}


def test_modify_subgraph_terminal(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node

    This test specifically the terminal node
    """

    subgraph = mmodel_G.subgraph(["multiply", "poly"])

    def mock_obj(c, x, y):
        return

    graph = util.modify_subgraph(mmodel_G, subgraph, "test", mock_obj, [])

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    assert graph.nodes["test"] == {
        "base_obj": mock_obj,
        "modifiers": [],
        "func": mock_obj,
        "returns": [],
        "sig": inspect.signature(mock_obj),
    }

    # Test the edge attributes
    assert graph.edges["add", "test"]["val"] == ["c"]
    assert graph.edges["subtract", "test"]["val"] == []


def test_modify_subgraph_middle(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node

    This test specifically the middle node
    """

    subgraph = mmodel_G.subgraph(["multiply", "subtract"])

    def mock_obj(c, x, y):
        return x + y

    graph = util.modify_subgraph(mmodel_G, subgraph, "test", mock_obj, ["e"])

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    assert graph.nodes["test"] == {
        "base_obj": mock_obj,
        "modifiers": [],
        "func": mock_obj,
        "returns": ["e"],
        "sig": inspect.signature(mock_obj),
    }

    # Test the edge attributes
    assert graph.edges["add", "test"]["val"] == ["c"]
    assert graph.edges["test", "poly"]["val"] == ["e"]


def test_modify_subgraph_none_returns(mmodel_G):
    """Test subgraph modification when returns are not specified

    This test specifically the middle node
    """

    subgraph = mmodel_G.subgraph(["multiply", "poly"])

    def mock_obj(c, x, y):
        return

    mock_obj.returns = ["e"]

    graph = util.modify_subgraph(mmodel_G, subgraph, "test", mock_obj)

    assert graph.nodes["test"] == {
        "base_obj": mock_obj,
        "modifiers": [],
        "func": mock_obj,
        "returns": ["e"],
        "sig": inspect.signature(mock_obj),
    }


def test_modify_subgraph_none_returns_fails(mmodel_G):
    """Test subgraph modification when returns are not specified

    The method fails when the subgraph node does not have a
    return attribute
    """

    subgraph = mmodel_G.subgraph(["multiply", "poly"])

    def mock_obj(c, x, y):
        return

    with pytest.raises(Exception, match="'subgraph_returns' not defined"):
        util.modify_subgraph(mmodel_G, subgraph, "test", mock_obj)


def test_modify_node(mmodel_G):
    """Test modify_node

    Test if the node have the correct signature and result
    """

    def mock_obj(c, x, y):
        return x + y

    def mod(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs) + 1

        return wrapped

    mod_G = util.modify_node(mmodel_G, "subtract", [(mod, {})], ["g"])

    # add one to the final value
    assert mod_G.nodes["subtract"]["func"](1, 2) == 0
    # make sure the edge value is updated
    assert mod_G["subtract"]["poly"]["val"] == ["g"]


def test_is_node_attr_defined():
    """Test is_node_attr_defined"""

    # all nodes defined
    g = nx.DiGraph()
    g.add_node(1, weight=0.5)
    g.add_node(2, weight=0.2)

    assert util.is_node_attr_defined(g, "weight")

    # missing attribute
    g = nx.DiGraph()
    g.add_node(1, weight=0.5)
    g.add_node(2)

    assert not util.is_node_attr_defined(g, "weight")


def test_is_edge_attr_defined():
    """Test is_edge_attr_defined"""

    # all nodes defined
    g = nx.DiGraph()
    g.add_edge(1, 2, weight=0.5)
    g.add_edge(2, 3, weight=0.2)

    assert util.is_edge_attr_defined(g, "weight")

    # missing attribute
    g = nx.DiGraph()
    g.add_edge(1, 2, weight=0.5)
    g.add_edge(2, 3)

    assert not util.is_edge_attr_defined(g, "weight")
