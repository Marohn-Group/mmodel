import math
import operator
import numpy as np
from mmodel.node import Node
from mmodel.group import ModelGroup
from mmodel.handler import BasicHandler
import pytest
from textwrap import dedent


@pytest.fixture
def node_objects():
    return [
        Node("add", np.add, inputs=["a", "h"], output="c"),
        Node("subtract", operator.sub, inputs=["c", "d"], output="e"),
        Node("power", math.pow, inputs=["c", "f"], output="g"),
        Node("multiply", np.multiply, inputs=["e", "g"], output="k", output_unit="m^2"),
        Node("log", math.log, inputs=["c", "b"], output="m"),
    ]


@pytest.fixture
def grouped_edges():
    return [
        ("add", ["subtract", "power", "log"]),
        (["subtract", "power"], "multiply"),
    ]


def test_model_construction(node_objects, grouped_edges):
    """Test the model construction."""

    instruction = {
        "grouped_edges": grouped_edges,
        "doc": "Test individual docstring.",
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        doc="Test group description.",
    )

    assert group.doc == "Test group description."
    assert group.__doc__ == "Test group description."
    assert group.models["test"].doc == "Test individual docstring."
    assert group.models["test"].graph.name == "test_graph"
    assert group.models["test"].group == "test_group_object"
    assert repr(group) == "<mmodel.group.ModelGroup 'test_group_object'>"


def test_model_defaults(node_objects, grouped_edges):
    """Test the model model_defaults property of the group."""

    instruction = {
        "grouped_edges": grouped_edges,
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        {"doc": "Test model doc."},
        "Test group description.",
    )

    assert group.models["test"].doc == "Test model doc."


def test_model_model_defaults_overwritten(node_objects, grouped_edges):
    """Test the model_defaults property of the group overwritten."""

    instruction = {
        "grouped_edges": grouped_edges,
        "doc": "Test individual model_defaults.",
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        {"doc": "Test model doc."},
        doc="Test group description.",
    )

    assert group.models["test"].doc == "Test individual model_defaults."


def test_group_str_representation(node_objects, grouped_edges):
    """Test the str representation of the group."""

    group_str = """\
    test_group_object
    models: ['test']
    nodes: ['add', 'subtract', 'power', 'multiply', 'log']

    Test group description."""

    instruction = {
        "grouped_edges": grouped_edges,
        "doc": "Test instruction.",
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        doc="Test group description.",
    )

    assert str(group) == dedent(group_str)

    group_str = """\
    test_group
    models: None
    nodes: ['add', 'subtract', 'power', 'multiply', 'log']"""

    group = ModelGroup("test_group", node_objects, "")
    assert str(group) == dedent(group_str)


def test_model_str_representation(node_objects, grouped_edges):
    """Test the str representation of the model.

    Test the group information is added to the model object.
    """

    model_str = """\
    test(a, b, d, f, h)
    returns: (k, m)
    group: test_group_object
    graph: test_graph
    handler: BasicHandler
    
    Test instruction."""

    instruction = {
        "grouped_edges": grouped_edges,
        "doc": "Test instruction.",
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        doc="Test group description.",
    )

    assert str(group.models["test"]) == dedent(model_str)


def test_model_KeyError(node_objects, grouped_edges):
    """Test the model KeyError when the model does not exist."""

    instruction = {
        "grouped_edges": grouped_edges,
        "doc": "Test instruction.",
        "handler": BasicHandler,
    }
    group = ModelGroup(
        "test_group_object",
        node_objects,
        {"test": instruction},
        doc="Test group description.",
    )

    with pytest.raises(KeyError, match="'test2'"):
        group.models["test2"]


def test_node_error(node_objects, grouped_edges):
    """Test the KeyError when edges contain non-existing nodes."""

    grouped_edges.append(["test_node", "test_node"])

    instruction = {"grouped_edges": grouped_edges, "doc": "Test instruction."}

    with pytest.raises(KeyError, match="node 'test_node' not found"):
        ModelGroup(
            "test_group_object",
            node_objects,
            {"test": instruction},
            doc="Test group description.",
        )


def test_edit(node_objects, grouped_edges):
    """Test the edit method of the group."""

    instruction = {"grouped_edges": grouped_edges, "handler": BasicHandler}
    group = ModelGroup(
        "Test_group",
        doc="Test group description.",
        node_objects=node_objects,
        model_recipes={"test": instruction},
        model_defaults={"doc": "Test model doc."},
    )

    new_group = group.edit(model_defaults={"doc": "New group doc."})
    assert new_group.models["test"].doc == "New group doc."
