"""Test graph operations

1. `test_param_sorter` - test `param_sorter` result
2. `test_param_sorter_order` - test if parameters are sorted
    correctly with `param_sorter`
3. `test_graph_signature` - test graph_signature
4. `test_graph_returns` - test graph_returns
5. `test_graph_returns` - test graph_returns
6. `test_parameter_c` - test graph_returns
7. `test_h5_read` - test reading h5 data
8. `test_h5_write` - test reading 
"""

import inspect
import pytest
import random
import mmodel.utility as util
from collections import OrderedDict
from inspect import Parameter


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


def test_graph_signature(mmodel_graph, mmodel_signature):
    """Test graph_signature

    There are two functions in the mmodel_graph have parameter
    'b' - one with default and one without. The final signature
    should have default value.
    """

    assert util.graph_signature(mmodel_graph) == mmodel_signature


def test_graph_returns(mmodel_graph):
    """Test graph_returns"""

    assert util.graph_returns(mmodel_graph) == ["k", "m"]


def test_graph_topological_sort(mmodel_graph):
    """Test graph_topological_sort

    The order should be
    add, subtract, multiply, log, poly

    each node should be (node, attr), where node is the name
    of the node, attr is a dictionary of attributes
    """

    order = util.graph_topological_sort(mmodel_graph)

    nodes = []

    for node, attr in order:
        assert isinstance(attr, dict)
        assert sorted(list(attr)) == ["node_obj", "return_params", "signature"]
        nodes.append(node)

    assert nodes == ["add","subtract", "multiply", "log", "poly"]


def test_param_counter(mmodel_graph):
    """Test param_counter"""

    counter = util.param_counter(mmodel_graph)

    assert counter == {"a": 1, "b": 2, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1}
