import inspect
import pytest
import random
from collections import OrderedDict
from inspect import Parameter
import networkx as nx
import mmodel.utility as util
from mmodel.node import Node


@pytest.fixture
def func():
    def example_func(a, c, b=2, *args, d, e=10, **kwargs):
        return a + b + c + d + e + sum(args) + sum(kwargs.values())

    return example_func


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
def test_param_sorter(parameter, result, func):
    """Test param_sorter result."""

    params = inspect.signature(func).parameters
    assert util.param_sorter(params[parameter]) == result


def test_param_sorter_order(func):
    """Test param_sorter sorting order.

    The correct order is a, b, *args, c, **kwargs, d=10.s
    """

    params = inspect.signature(func).parameters
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


def test_modelgraph_signature(mmodel_G, mmodel_signature):
    """Test graph_signature.

    Two functions in the mmodel_G have the parameter
    'b' - one with default and one without. The final signature
    should have a default value.
    """

    assert util.modelgraph_signature(mmodel_G) == mmodel_signature


def test_parse_parameters():
    """Test parse_parameters.

    Here, we test when the default value is at the end or in the middle.
    """

    sig, porder, dargs = util.parse_parameters(["a", "b", ("c", 2)])
    assert porder == ["a", "b", "c"]
    assert list(sig.parameters.keys()) == ["a", "b", "c"]
    assert sig.parameters["c"].default == 2
    assert dargs == {"c": 2}

    sig, porder, dargs = util.parse_parameters(["a", ("b", 3), ("c", 2), "d"])
    assert porder == ["a", "b", "c", "d"]
    assert list(sig.parameters.keys()) == ["a", "d", "b", "c"]
    assert sig.parameters["b"].default == 3
    assert sig.parameters["c"].default == 2
    assert dargs == {"b": 3, "c": 2}


def test_modelgraph_returns(mmodel_G):
    """Test graph_returns."""

    assert util.modelgraph_returns(mmodel_G) == ["k", "m"]


def test_modelgraph_returns_None():
    """Test graph_returns if node functions don't have output."""

    from mmodel.graph import Graph

    G = Graph()
    G.add_node("Test")
    G.set_node_object(Node("Test", lambda x: None, output=None))

    assert util.modelgraph_returns(G) == []


def test_graph_topological_sort(mmodel_G):
    """Test graph_topological_sort.

    The order is: add, subtract, multiply, log, power.

    each node should be (node, attr), where the node is the name
    of the node, attr is a dictionary of attributes.
    """

    order = util.graph_topological_sort(mmodel_G)

    assert list(list(zip(*order))[0]) == ["add", "subtract", "power", "log", "multiply"]


def test_param_counter(mmodel_G):
    """Test param_counter."""

    counter = util.param_counter(mmodel_G, [])

    assert counter == {"a": 1, "b": 1, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1}


def test_param_counter_add_returns(mmodel_G):
    """Test param_counter with added returns."""

    counter = util.param_counter(mmodel_G, ["c", "g"])

    assert counter == {"a": 1, "b": 1, "c": 4, "d": 1, "e": 1, "f": 1, "g": 2}


def test_replace_subgraph_terminal(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node.

    This tests specifically the terminal node.
    """

    subgraph = mmodel_G.subgraph(["multiply", "power"])

    def func(c, e, x, y):
        """Function docstring."""
        return

    node = Node("test", func)
    graph = util.replace_subgraph(mmodel_G, subgraph, node)

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    # Test the edge attributes
    assert graph.edges["add", "test"]["output"] == "c"
    assert graph.edges["subtract", "test"]["output"] == "e"


def test_replace_subgraph_middle(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node.

    This test specifically the middle node.
    """

    subgraph = mmodel_G.subgraph(["subtract", "power"])

    def func(c, x, y):
        """Function docstring."""
        return x + y

    node = Node("test", func, output="e")

    # combine the nodes subtract and power to a "test" node
    graph = util.replace_subgraph(mmodel_G, subgraph, node)

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    # Test the edge attributes
    assert graph.edges["add", "test"]["output"] == "c"
    # test node is connected to multiply node
    assert graph.edges["test", "multiply"]["output"] == "e"


def test_modify_node(mmodel_G, value_modifier):
    """Test modify_node.

    Test if the node has the correct signature and result.
    """

    mod_G = mmodel_G.edit_node("subtract", modifiers=[value_modifier(value=1)])

    # add one to the final value
    assert mod_G.nodes["subtract"]["node_object"](1, 2) == 0


def test_is_node_attr_defined():
    """Test is_node_attr_defined."""

    # all nodes defined
    g = nx.DiGraph()
    g.add_node(1, weight=0.5)
    g.add_node(2, weight=0.2)

    assert util.is_node_attr_defined(g, "weight")

    # missing attribute
    g = nx.DiGraph()
    g.add_node(1, w=0.5)
    g.add_node(2)
    g.add_node(3)

    with pytest.raises(
        Exception,
        match=r"invalid graph: attribute 'w' is not defined for node\(s\) \[2, 3\]",
    ):
        util.is_node_attr_defined(g, "w")


def test_is_edge_attr_defined():
    """Test is_edge_attr_defined."""

    # all nodes defined
    g = nx.DiGraph()
    g.add_edge(1, 2, weight=0.5)
    g.add_edge(2, 3, weight=0.2)

    assert util.is_edge_attr_defined(g, "weight")

    # missing attribute
    g = nx.DiGraph()
    g.add_edge(1, 2, w=0.5)
    g.add_edge(2, 3)
    g.add_edge(3, 4)

    with pytest.raises(
        Exception,
        match=(
            r"invalid graph: attribute 'w' is "
            r"not defined for edge\(s\) \[\(2, 3\), \(3, 4\)\]"
        ),
    ):
        util.is_edge_attr_defined(g, "w")


def test_parse_functype(func):
    """Test parse_functype."""

    import numpy as np
    import math
    import operator

    assert util.parse_functype(func) == "function"
    assert util.parse_functype(math.acos) == "builtin_function_or_method"
    assert util.parse_functype(operator.add) == "builtin_function_or_method"
    assert util.parse_functype(np.sum) == "numpy._ArrayFunctionDispatcher"
    assert util.parse_functype(np.add) == "numpy.ufunc"
