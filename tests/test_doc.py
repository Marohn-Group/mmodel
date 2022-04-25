"""Test documentations throughout module
"""

# from mmodel import Model
from mmodel.doc import attr_to_doc
import pytest

GRAPH_REPR = """ModelGraph named 'test' with 5 nodes and 5 edges

test object

long description"""

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
def attribute_dict():

    attr_dict = {"name": "test", "doc": "docstring"}
    return attr_dict

def test_parse_description_doc(attribute_dict):
    """Test parse_description_doc function"""

    des_str = attr_to_doc(attribute_dict)
    assert des_str == "NAME - test\nDOC - docstring\n"

# def test_str_named(mmodel_G):
#     """Test the string value"""
#     assert (
#         str(mmodel_G)
#         == f"{type(mmodel_G).__name__} named 'test' with 5 nodes and 5 edges"
#     )


def test_graph_repr(mmodel_G):
    """Test graph representation"""

    assert str(mmodel_G) == GRAPH_REPR

# def test_parse_description_graph(description_list):
#     """Test parse_description_graph function"""

#     des_str = parse_description_graph(description_list)
#     assert des_str == "name: test\ldoc: docstring\l"





# def test_graph_description_list(mmodel_G):
#     """Test graph description"""

#     assert mmodel_G._short_description() == [("name", "test"), ("doc", "test object")]
#     assert mmodel_G._long_description(False) == [
#         ("name", "test"),
#         ("doc", "test object"),
#         ("graph type", "<class 'mmodel.graph.MGraph'>"),
#         ("parameters", "(a, d, f, b=2)"),
#         ("returns", "k, m"),
#     ]
#     assert mmodel_G._long_description() == [
#         ("name", "test"),
#         ("doc", "test object\n\nlong description"),
#         ("graph type", "<class 'mmodel.graph.MGraph'>"),
#         ("parameters", "(a, d, f, b=2)"),
#         ("returns", "k, m"),
#     ]


# def test_model_description_list(mmodel_G):
#     """Test model description"""

#     model = Model(mmodel_G)

#     assert model._short_description() == [
#         ("name", "test model"),
#         ("doc", "test object"),
#         ("model type", "Model"),
#     ]

#     assert model._long_description(False) == [
#         ("name", "test model"),
#         ("doc", "test object"),
#         ("model type", "<class 'mmodel.model.Model'>"),
#         ("parameters", "(a, d, f, b=2)"),
#         ("returns", "k, m"),
#     ]

#     assert model._long_description() == [
#         ("name", "test model"),
#         ("doc", "test object\n\nlong description"),
#         ("model type", "<class 'mmodel.model.Model'>"),
#         ("parameters", "(a, d, f, b=2)"),
#         ("returns", "k, m"),
#     ]



# def test_model_repr(mmodel_G):
#     """Test model representation"""

#     model = Model(mmodel_G)
#     assert repr(model) == MODEL_REPR
