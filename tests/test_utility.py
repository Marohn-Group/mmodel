import inspect
import pytest
import random
import mmodel.utility as util
from collections import OrderedDict
from inspect import Parameter
from tests.conftest import graph_equal
import networkx as nx
from functools import wraps
from textwrap import dedent


@pytest.fixture
def func():
    def example_func(a, c, b=2, *args, d, e=10, **kwargs):
        return

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
    """Test param_sorter result"""

    params = inspect.signature(func).parameters
    assert util.param_sorter(params[parameter]) == result


def test_param_sorter_order(func):
    """Test param_sorter sorting order

    the correct order is a, b, *args, c, **kwargs, d=10
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


def test_model_signature(mmodel_G, mmodel_signature):
    """Test graph_signature

    There are two functions in the mmodel_G have parameter
    'b' - one with default and one without. The final signature
    should have default value.
    """

    assert util.modelgraph_signature(mmodel_G) == mmodel_signature


def test_replace_signature(mmodel_signature):
    """Test replace signature"""

    replacement_dict = {"a_rep": ["a"], "f_rep": ["f", "g"]}
    signature = util.replace_signature(mmodel_signature, replacement_dict)

    assert "a_rep" in signature.parameters
    assert "a" not in signature.parameters
    assert "f_rep" in signature.parameters
    assert "f" not in signature.parameters
    assert "g" not in signature.parameters

    # make sure the original signature is not modified
    assert "a_rep" not in mmodel_signature.parameters


def test_parse_parameters():
    """Test parse_parameters

    Here we test when the default value is at the end or in the middle
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


def test_model_returns(mmodel_G):
    """Test graph_returns"""

    assert util.modelgraph_returns(mmodel_G) == ["k", "m"]


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
        assert sorted(list(attr)) == [
            "_func",
            "doc",
            "func",
            "functype",
            "modifiers",
            "output",
            "sig",
        ]
        nodes.append(node)

    assert nodes == ["add", "subtract", "poly", "log", "multiply"]


def test_param_counter(mmodel_G):
    """Test param_counter"""

    counter = util.param_counter(mmodel_G, [])

    assert counter == {"a": 1, "b": 1, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1}


def test_param_counter_add_returns(mmodel_G):
    """Test param_counter with added returns"""

    counter = util.param_counter(mmodel_G, ["c", "g"])

    assert counter == {"a": 1, "b": 1, "c": 4, "d": 1, "e": 1, "f": 1, "g": 2}


def test_replace_subgraph_terminal(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node

    This tests specifically the terminal node
    """

    subgraph = mmodel_G.subgraph(["multiply", "poly"])

    def func(c, e, x, y):
        """function docstring"""
        return

    graph = util.replace_subgraph(mmodel_G, subgraph, "test", func)

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    assert graph.nodes["test"] == {
        "_func": func,
        "modifiers": [],
        "func": func,
        "output": None,
        "sig": inspect.signature(func),
        "doc": "function docstring",
        "functype": "callable",
    }

    # Test the edge attributes
    assert graph.edges["add", "test"]["var"] == "c"
    assert graph.edges["subtract", "test"]["var"] == "e"


def test_replace_subgraph_middle(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node

    This test specifically the middle node
    """

    subgraph = mmodel_G.subgraph(["subtract", "poly"])

    def func(c, x, y):
        """function docstring"""
        return x + y

    # combine the nodes subtract and poly to a "test" node
    graph = util.replace_subgraph(mmodel_G, subgraph, "test", func, "e")

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph

    assert graph.nodes["test"] == {
        "_func": func,
        "modifiers": [],
        "func": func,
        "output": "e",
        "sig": inspect.signature(func),
        "doc": "function docstring",
        "functype": "callable",
    }

    # Test the edge attributes
    assert graph.edges["add", "test"]["var"] == "c"
    # test node is connected to multiply node
    assert graph.edges["test", "multiply"]["var"] == "e"


def test_modify_node(mmodel_G):
    """Test modify_node

    Test if the node have the correct signature and result
    """

    def mod(func, a):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs) + a

        return wrapped

    mod_G = util.modify_node(mmodel_G, "subtract", modifiers=[(mod, {"a": 1})])

    # add one to the final value
    assert mod_G.nodes["subtract"]["func"](1, 2) == 0


def test_modify_node_inplace(mmodel_G):
    """Test modify_node to modify in place"""

    def mod(func, a):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs) + a

        return wrapped

    mod_G = util.modify_node(
        mmodel_G, "subtract", modifiers=[(mod, {"a": 1})], inplace=True
    )

    # test the original graph
    assert mod_G.nodes["subtract"]["func"](1, 2) == 0
    assert mmodel_G.nodes["subtract"]["func"](1, 2) == 0


def test_parse_modifiers():
    """Test pase_modifier outputs the correct string

    Here to test string, list and tuples
    """

    def mod1(func, parameter):
        return

    def mod2(func, param1, param2):
        return

    modifier_str = """\
      modifiers:
        - mod1(test)
        - mod2([1, 2, 3], (1, 2))"""

    modifiers = [
        (mod1, {"parameter": "test"}),
        (mod2, {"param1": [1, 2, 3], "param2": (1, 2)}),
    ]

    modifier_str_list = ["modifiers:", "\t- mod1(test)", "\t- mod2([1, 2, 3], (1, 2))"]
    assert util.parse_modifiers(modifiers) == modifier_str_list


def test_parse_modifier_empty():
    """Test pase_modifier outputs None when there is no modifier"""

    assert util.parse_modifiers([]) == []


def test_is_node_attr_defined():
    """Test is_node_attr_defined"""

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
        match=r"invalid graph: weight \('w'\) is not defined for node\(s\) \[2, 3\]",
    ):
        util.is_node_attr_defined(g, "w", "weight")


def test_is_edge_attr_defined():
    """Test is_edge_attr_defined"""

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
            r"invalid graph: weight \('w'\) is "
            r"not defined for edge\(s\) \[\(2, 3\), \(3, 4\)\]"
        ),
    ):
        util.is_edge_attr_defined(g, "w", "weight")
