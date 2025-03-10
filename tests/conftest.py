import pytest
from inspect import Signature, Parameter
import networkx as nx
from mmodel.graph import Graph
import operator
import math
import numpy as np
from mmodel.node import Node
from functools import wraps
from mmodel.model import Model
from mmodel.handler import BasicHandler


# define the global functions for two graph
# both graphs reference the same set of functions in nodes
# in graph testing, they should be equal


def addition(a, constant=2):
    """Add a constant to the value a."""
    return a + constant


def logarithm(c, b):
    """Logarithm operation."""
    return math.log(c, b)


add_node = Node("add", addition, output="c")
sub_node = Node("subtract", operator.sub, ["c", "d"], output="e")
power_node = Node("power", math.pow, ["c", "f"], output="g")
multi_node = Node("multiply", np.multiply, ["e", "g"], output="k")
log_node = Node("log", logarithm, output="m")


@pytest.fixture()
def standard_G():
    """Standard test graph generated using DiGraph.
    The inputs are:
    a, b, d, f
    The results are:
    k = (a + 2 - d)(a + 2)^f
    m = log(a + 2, b)
    """

    node_list = [
        (
            "add",
            {"node_object": add_node, "signature": add_node.signature, "output": "c"},
        ),
        (
            "subtract",
            {"node_object": sub_node, "signature": sub_node.signature, "output": "e"},
        ),
        (
            "power",
            {
                "node_object": power_node,
                "signature": power_node.signature,
                "output": "g",
            },
        ),
        (
            "multiply",
            {
                "node_object": multi_node,
                "signature": multi_node.signature,
                "output": "k",
            },
        ),
        (
            "log",
            {"node_object": log_node, "signature": log_node.signature, "output": "m"},
        ),
    ]

    edge_list = [
        ("add", "subtract", {"output": "c"}),
        ("subtract", "multiply", {"output": "e"}),
        ("add", "power", {"output": "c"}),
        ("power", "multiply", {"output": "g"}),
        ("add", "log", {"output": "c"}),
    ]

    G = nx.DiGraph(name="test_graph")
    G.graph["graph_module"] = "mmodel"  # for comparison
    G.graph["node_type"] = Node

    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    return G


@pytest.fixture()
def mmodel_G():
    """Mock test graph generated using Graph.

    The results are:
    k = (a + 2 - d)(a + b)^f
    m = log(a + 2, b)
    """

    grouped_edges = [
        ("add", ["subtract", "power", "log"]),
        (["subtract", "power"], "multiply"),
    ]

    node_objects = [add_node, sub_node, power_node, multi_node, log_node]

    G = Graph(name="test_graph")
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


@pytest.fixture
def model_instance(mmodel_G):
    """Construct a model_instance."""
    description = (
        "A long description that tests if the model module"
        " wraps the Model output string description at 90 characters."
    )
    return Model("model_instance", mmodel_G, BasicHandler, doc=description)


@pytest.fixture
def value_modifier():
    """Return a modifier function that adds value to the result."""

    def add_value(value):
        def mod(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs) + value

            return wrapped

        mod.metadata = f"add_value(value={value})"
        return mod

    return add_value


def graph_equal(G1, G2):
    """Test if graphs have the same nodes, edges, and attributes.
    The node_object object is deep copied, so the object ID is different.

    Dictionary comparison does not care about key orders.
    """

    for node in G1.nodes:
        assert node in G2.nodes
        for attr in G1.nodes[node]:
            if attr == "node_object":
                assert G1.nodes[node][attr].__dict__ == G2.nodes[node][attr].__dict__
            else:
                assert G1.nodes[node][attr] == G2.nodes[node][attr]

    assert dict(G1.edges) == dict(G2.edges)

    # test graph attributes
    assert G1.graph == G2.graph
    assert G1.name == G2.name

    return True
