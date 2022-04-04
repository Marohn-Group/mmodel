"""Configuration for testing

The configuration file provides several default graph fixtures
and test functions

1. `standard_G` - test graph generated using DiGraph, scope: function
2. `mmodel_G` - test graph generated using ModelGraph. scope: function


"""


import pytest
from inspect import signature, Signature, Parameter
import networkx as nx
from mmodel.graph import MGraph
import math
from networkx.utils import nodes_equal, edges_equal


@pytest.fixture()
def standard_G():
    """Standard test graph generated using DiGraph"""

    def addition(a, b=2):
        return a + b

    def subtraction(c, d):
        return c - d

    def multiplication(c, f):
        return c * f

    def polynomial(e, g):
        return e * g

    def logarithm(c, b):
        return math.log(c, b)

    node_list = [
        (
            "add",
            {
                "node_obj": addition,
                "return_params": ["c"],
                "signature": signature(addition),
            },
        ),
        (
            "subtract",
            {
                "node_obj": subtraction,
                "return_params": ["e"],
                "signature": signature(subtraction),
            },
        ),
        (
            "multiply",
            {
                "node_obj": multiplication,
                "return_params": ["g"],
                "signature": signature(multiplication),
            },
        ),
        (
            "poly",
            {
                "node_obj": polynomial,
                "return_params": ["k"],
                "signature": signature(polynomial),
            },
        ),
        (
            "log",
            {
                "node_obj": logarithm,
                "return_params": ["m"],
                "signature": signature(logarithm),
            },
        ),
    ]

    edge_list = [
        ("add", "subtract", {"interm_params": ["c"]}),
        ("subtract", "poly", {"interm_params": ["e"]}),
        ("add", "multiply", {"interm_params": ["c"]}),
        ("multiply", "poly", {"interm_params": ["g"]}),
        ("add", "log", {"interm_params": ["c"]}),
    ]

    G = nx.DiGraph(name="test", doc="test object")

    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    return G


@pytest.fixture()
def mmodel_G():
    """Mock test graph generated using ModelGraph"""

    def addition(a, b=2):
        return a + b

    def subtraction(c, d):
        return c - d

    def multiplication(c, f):
        return c * f

    def polynomial(e, g):
        return e * g

    def logarithm(c, b):
        return math.log(c, b)

    G = MGraph("test", "test object")

    # class MockGraph(ModelGraph):
    node_list = [
        ("add", {"node_obj": addition, "return_params": ["c"]}),
        ("subtract", {"node_obj": subtraction, "return_params": ["e"]}),
        ("multiply", {"node_obj": multiplication, "return_params": ["g"]}),
        ("poly", {"node_obj": polynomial, "return_params": ["k"]}),
        ("log", {"node_obj": logarithm, "return_params": ["m"]}),
    ]

    edge_list = [
        ("add", "subtract", {"interm_params": ["c"]}),
        ("subtract", "poly", {"interm_params": ["e"]}),
        ("add", "multiply", {"interm_params": ["c"]}),
        ("multiply", "poly", {"interm_params": ["g"]}),
        ("add", "log", {"interm_params": ["c"]}),
    ]

    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    return G


@pytest.fixture(scope="module")
def mmodel_signature():
    """The default signature of the mmodel_G models"""

    param_list = [
        Parameter("a", 1),
        Parameter("d", 1),
        Parameter("f", 1),
        Parameter("b", 1, default=2),
    ]

    return Signature(param_list)


def graphs_equal(G1, G2):
    """Test if graphs have the same nodes, edges and attributes"""

    assert nodes_equal(G1._node, G2._node)
    # assert edges_equal(mmodel_G._adj, standard_G._adj)

    assert G1._pred == G2._pred
    assert G1._succ == G2._succ

    # test graph attributes
    assert G1.graph == G2.graph
    assert G1.name == G2.name
