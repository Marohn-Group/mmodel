"""Test documentations throughout module
"""

from mmodel import Model
from mmodel.doc import parse_description_doc, parse_description_graph
import pytest

GRAPH_REPR = """MGraph instance

NAME
    test
DOC
    test object
    
    long description
GRAPH TYPE
    <class 'mmodel.graph.MGraph'>
PARAMETERS
    (a, d, f, b=2)
RETURNS
    k, m
"""

MODEL_REPR = """Model instance

NAME
    test model
DOC
    test object
    
    long description
MODEL TYPE
    <class 'mmodel.model.Model'>
PARAMETERS
    (a, d, f, b=2)
RETURNS
    k, m
"""


@pytest.fixture
def description_list():

    des_list = [("name", "test"), ("doc", "docstring")]

    return des_list


def test_parse_description_graph(description_list):
    """Test parse_description_graph function"""

    des_str = parse_description_graph(description_list)
    assert des_str == "name: test\ldoc: docstring\l"


def test_parse_description_doc(description_list):
    """Test parse_description_doc function"""

    des_str = parse_description_doc(description_list)
    assert des_str == "NAME\n\ttest\nDOC\n\tdocstring\n"


def test_graph_description_list(mmodel_G):
    """Test graph description"""

    assert mmodel_G._short_description() == [("name", "test"), ("doc", "test object")]
    assert mmodel_G._long_description(False) == [
        ("name", "test"),
        ("doc", "test object"),
        ("graph type", "<class 'mmodel.graph.MGraph'>"),
        ("parameters", "(a, d, f, b=2)"),
        ("returns", "k, m"),
    ]
    assert mmodel_G._long_description() == [
        ("name", "test"),
        ("doc", "test object\n\nlong description"),
        ("graph type", "<class 'mmodel.graph.MGraph'>"),
        ("parameters", "(a, d, f, b=2)"),
        ("returns", "k, m"),
    ]


def test_model_description_list(mmodel_G):
    """Test model description"""

    model = Model(mmodel_G)

    assert model._short_description() == [
        ("name", "test model"),
        ("doc", "test object"),
        ("model type", "Model"),
    ]

    assert model._long_description(False) == [
        ("name", "test model"),
        ("doc", "test object"),
        ("model type", "<class 'mmodel.model.Model'>"),
        ("parameters", "(a, d, f, b=2)"),
        ("returns", "k, m"),
    ]

    assert model._long_description() == [
        ("name", "test model"),
        ("doc", "test object\n\nlong description"),
        ("model type", "<class 'mmodel.model.Model'>"),
        ("parameters", "(a, d, f, b=2)"),
        ("returns", "k, m"),
    ]


def test_graph_repr(mmodel_G):
    """Test graph representation"""

    assert repr(mmodel_G) == GRAPH_REPR


def test_model_repr(mmodel_G):
    """Test model representation"""

    model = Model(mmodel_G)
    assert repr(model) == MODEL_REPR
