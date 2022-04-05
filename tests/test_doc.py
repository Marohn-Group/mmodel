"""Test draw graph functions

MGraph.draw_graph and Model.draw_graph methods are both
tested here.

"""

from mmodel import Model
from mmodel.doc import helper

graph_doc_long = """test: test object
long docstring
input parameters: (a, d, f, b=2)
return parameters: k, m
"""

graph_model_long = """test model: test object
long docstring
class: Model
signature: (a, d, f, b=2)
returns: k, m
"""

def test_helper(capsys):
    """Test the helper instance"""

    def func(a, b):
        """Test doc"""
        return a, b

    func.doc_long = "test docstring"

    helper(func)
    captured_combined = capsys.readouterr()
    help(func)
    captured = capsys.readouterr()
    assert captured_combined.out == "test docstring" + captured.out

def test_graph_doc(mmodel_G):
    """Test graph doc"""

    assert mmodel_G.doc_short == "test: test object\n"
    assert mmodel_G.doc_long == graph_doc_long


def test_graph_help(mmodel_G, capsys):
    """Test graph help"""
    mmodel_G.help
    captured_combined = capsys.readouterr()
    help(mmodel_G)
    captured = capsys.readouterr()
    assert captured_combined.out == graph_doc_long + captured.out


def test_model_doc(mmodel_G):
    """Test model doc"""

    model = Model(mmodel_G)

    assert model.doc_short == "test model: test object\nclass: Model\n"
    assert model.doc_long == graph_model_long


def test_model_help(mmodel_G, capsys):
    """Test model help"""
    model = Model(mmodel_G)
    model.help
    captured_combined = capsys.readouterr()
    help(model)
    captured = capsys.readouterr()
    assert captured_combined.out == graph_model_long + captured.out
