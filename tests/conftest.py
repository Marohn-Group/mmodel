"""Configuration for testing

The configuration file provides several default graph fixtures
and test functions

1. `standard_G` - test graph generated using DiGraph, scope: function
2. `mmodel_G` - test graph generated using ModelGraph. scope: function
"""


import pytest
from inspect import signature, Signature, Parameter
import networkx as nx
from mmodel.graph import ModelGraph
import math


# define the global functions for two graph
# both graphs references the same set of functions in nodes
# in graph testing they should be equal


def addition(a, b=2):
    return a + b


def subtraction(c, d):
    return c - d


def polynomial(c, f):
    return c**f


def multiplication(e, g):
    return e * g


def logarithm(c, b):
    return math.log(c, b)


@pytest.fixture()
def standard_G():
    """Standard test graph generated using DiGraph

    The results are:
    k = (a + b - d)(a + b)^f
    m = log(a + b, b)
    """

    node_list = [
        (
            "add",
            {
                "base_func": addition,
                "func": addition,
                "output": "c",
                "sig": signature(addition),
                "modifiers": [],
            },
        ),
        (
            "subtract",
            {
                "base_func": subtraction,
                "func": subtraction,
                "output": "e",
                "sig": signature(subtraction),
                "modifiers": [],
            },
        ),
        (
            "poly",
            {
                "base_func": polynomial,
                "func": polynomial,
                "output": "g",
                "sig": signature(polynomial),
                "modifiers": [],
            },
        ),
        (
            "multiply",
            {
                "base_func": multiplication,
                "func": multiplication,
                "output": "k",
                "sig": signature(multiplication),
                "modifiers": [],
            },
        ),
        (
            "log",
            {
                "base_func": logarithm,
                "func": logarithm,
                "output": "m",
                "sig": signature(logarithm),
                "modifiers": [],
            },
        ),
    ]

    edge_list = [
        ("add", "subtract", {"val": "c"}),
        ("subtract", "multiply", {"val": "e"}),
        ("add", "poly", {"val": "c"}),
        ("poly", "multiply", {"val": "g"}),
        ("add", "log", {"val": "c"}),
    ]

    G = nx.DiGraph(name="test graph")
    G.graph["type"] = "ModelGraph"  # for comparison

    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    return G


@pytest.fixture()
def mmodel_G():
    """Mock test graph generated using ModelGraph

    The results are:
    k = (a + b - d)(a + b)^f
    m = log(a + b, b)
    """

    grouped_edges = [
        ("add", ["subtract", "poly", "log"]),
        (["subtract", "poly"], "multiply"),
    ]

    node_objects = [
        ("add", addition, "c"),
        ("subtract", subtraction, "e"),
        ("poly", polynomial, "g"),
        ("multiply", multiplication, "k"),
        ("log", logarithm, "m"),
    ]

    G = ModelGraph(name="test graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)
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


def graph_equal(G1, G2):
    """Test if graphs have the same nodes, edges and attributes

    Dictionary comparison does not care about key orders
    """

    assert dict(G1.nodes) == dict(G2.nodes)
    assert dict(G1.edges) == dict(G2.edges)

    # test graph attributes
    assert G1.graph == G2.graph
    assert G1.name == G2.name

    return True
