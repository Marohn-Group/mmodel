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
from mmodel.parser import node_parser
import math


# define the global functions for two graph
# both graphs reference the same set of functions in nodes
# in graph testing they should be equal


def addition(a, constant=2):
    """Add a constant to the value a."""
    return a + constant


def subtraction(c, d):
    """Subtraction operation."""
    return c - d


def power(c, f):
    """The value of c raise to the power of f."""
    return c**f


def multiplication(e, g):
    """Multiply e and g."""
    return e * g


def logarithm(c, b):
    """Logarithm operation."""
    return math.log(c, b)


@pytest.fixture()
def standard_G():
    """Standard test graph generated using DiGraph.

    The results are:
    k = (a + 2 - d)(a + 2)^f
    m = log(a + 2, b)
    """

    node_list = [
        (
            "add",
            {
                "_func": addition,
                "func": addition,
                "output": "c",
                "sig": signature(addition),
                "modifiers": [],
                "doc": "Add a constant to the value a.",
                "functype": "callable",
            },
        ),
        (
            "subtract",
            {
                "_func": subtraction,
                "func": subtraction,
                "output": "e",
                "sig": signature(subtraction),
                "modifiers": [],
                "doc": "Subtraction operation.",
                "functype": "callable",
            },
        ),
        (
            "power",
            {
                "_func": power,
                "func": power,
                "output": "g",
                "sig": signature(power),
                "modifiers": [],
                "doc": "The value of c raise to the power of f.",
                "functype": "callable",
            },
        ),
        (
            "multiply",
            {
                "_func": multiplication,
                "func": multiplication,
                "output": "k",
                "sig": signature(multiplication),
                "modifiers": [],
                "doc": "Multiply e and g.",
                "functype": "callable",
            },
        ),
        (
            "log",
            {
                "_func": logarithm,
                "func": logarithm,
                "output": "m",
                "sig": signature(logarithm),
                "modifiers": [],
                "doc": "Logarithm operation.",
                "functype": "callable",
            },
        ),
    ]

    edge_list = [
        ("add", "subtract", {"var": "c"}),
        ("subtract", "multiply", {"var": "e"}),
        ("add", "power", {"var": "c"}),
        ("power", "multiply", {"var": "g"}),
        ("add", "log", {"var": "c"}),
    ]

    G = nx.DiGraph(name="test_graph", parser=node_parser)
    G.graph["type"] = "ModelGraph"  # for comparison

    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    return G


@pytest.fixture()
def mmodel_G():
    """Mock test graph generated using ModelGraph.

    The results are:
    k = (a + 2 - d)(a + b)^f
    m = log(a + 2, b)
    """

    grouped_edges = [
        ("add", ["subtract", "power", "log"]),
        (["subtract", "power"], "multiply"),
    ]

    node_objects = [
        ("add", addition, "c"),
        ("subtract", subtraction, "e"),
        ("power", power, "g"),
        ("multiply", multiplication, "k"),
        ("log", logarithm, "m"),
    ]

    G = ModelGraph(name="test_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)
    return G


@pytest.fixture(scope="module")
def mmodel_signature():
    """The default signature of the mmodel_G models."""

    param_list = [
        Parameter("a", 1),
        Parameter("b", 1),
        Parameter("d", 1),
        Parameter("f", 1),
    ]

    return Signature(param_list)


def graph_equal(G1, G2):
    """Test if graphs have the same nodes, edges, and attributes.

    Dictionary comparison does not care about key orders.
    """

    assert dict(G1.nodes) == dict(G2.nodes)
    assert dict(G1.edges) == dict(G2.edges)

    # test graph attributes
    # ModelGraph adds parser attribute, here we test if the functions
    # are the same.
    for key in G1.graph:
        if key == "parser":
            assert G1.graph[key]._parser_dict == G2.graph[key]._parser_dict
        else:
            assert G1.graph[key] == G2.graph[key]
    assert G1.name == G2.name

    return True
