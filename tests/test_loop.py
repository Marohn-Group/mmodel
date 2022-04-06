"""
Testing the loop module
"""

import py
import pytest
from mmodel.loop import subgraph_from_params, redirect_edges, basic_loop
from tests.conftest import graphs_equal
import inspect

@pytest.fixture
def mock_func():
    def func(a, b, c=2):
        """Test docstring"""
        return a + b + c

    return func


def test_subgraph_from_params(mmodel_G):
    """Test two different subgraphs"""

    subgraph1 = subgraph_from_params(mmodel_G, ["f"])
    subgraph2 = mmodel_G.subgraph(["multiply", "poly"])

    # have the same copy
    graphs_equal(subgraph1, subgraph2)
    # retains oringinal graph
    assert subgraph1._graph == mmodel_G

    subgraph3 = subgraph_from_params(mmodel_G, ["f", "g"])
    graphs_equal(subgraph3, subgraph2)

    subgraph4 = subgraph_from_params(mmodel_G, ["a"])
    graphs_equal(subgraph4, mmodel_G)


def test_redirect_edges(mmodel_G):
    """Test redirect edges based on subgraph and subgraph node"""

    subgraph = mmodel_G.subgraph(["multiply", "poly"])

    def mock_obj(x, y):
        return

    graph = redirect_edges(mmodel_G, subgraph, "test", mock_obj, ["z"], ["f"])

    # a copy is created
    assert graph != mmodel_G
    assert "test" in graph
    assert graph.nodes["test"] == {
        "node_obj": mock_obj,
        "returns": ["z"],
        "signature": inspect.signature(mock_obj),
        "loop_params": ["f"],
        "has_subgraph": True,
        "has_loop": True
    }


def test_basic_loop(mock_func):
    """Test redirect edges based on subgraph and subgraph node"""

    mock_func._test_attr = "test"
    looped = basic_loop(mock_func, "b")

    assert looped(1, [1, 2, 3], 4) == [6, 7, 8]
    # check if default value works
    assert looped(1, [1, 2, 3]) == [4, 5, 6]
    # wraps decorator updates the docstring, checking that here
    assert looped.__doc__ == "Test docstring"
    assert looped._test_attr == "test"

    looped_default = basic_loop(mock_func, params=["c"])

    assert inspect.signature(looped_default).parameters['c'].default == [2]
    assert looped_default(0.1, 0.1) == [2.2]
    assert looped_default(0.1, 0.1, [3, 4]) == [3.2, 4.2]

def test_basic_loop_fails(mock_func):
    """Test redirect edges based on subgraph and subgraph node"""

    with pytest.raises(Exception, match="basic_loop accept one parameter at a time"):
        basic_loop(mock_func, ["b", "c"])

