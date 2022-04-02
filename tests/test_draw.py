"""Test draw_model function

draw_model returns a graphviz.DiGraph object, the tests consist of two parts
1. if draw model creates the correct dot string
"""

from mmodel.draw import draw_graph
from mmodel.model import Model
import pytest

dot_source = """digraph test {
graph [label=test labelloc=t ordering=out splines=ortho]
node [shape=box]
add
subtract
multiply
poly
log
add -> subtract
add -> multiply
add -> log
subtract -> poly
multiply -> poly
}"""



def test_draw_model_no_detail(mmodel_graph):
    """Test the model without the node detail"""

    dot_graph = draw_graph(mmodel_graph, title="test", show_detail=False)
    assert dot_graph.source.replace('\n', '').replace('\t', '') == dot_source.replace('\n', '')


def test_draw_model_detail(mmodel_graph):
    """Test the model with full node and edge detail"""

    dot_graph = draw_graph(mmodel_graph, title="test")
    assert "add\l\naddition(a, b=2)\lreturn c\l" in dot_graph.source


def test_draw_model_settings(mmodel_graph):
    """Test change model settings"""

    dot_graph = draw_graph(
        mmodel_graph,
        title="test",
        node_attr={"shape": "plaintext"},
        edge_attr={"label": "test"},
    )

    assert dot_graph.edge_attr == {"label": "test"}
    assert dot_graph.name == mmodel_graph.name
    assert dot_graph.filename == f"{mmodel_graph.name}.gv"
    assert "label=test" in dot_graph.source


@pytest.fixture
def model_instance(mmodel_graph):
    """Create Model object for the test"""
    return Model(mmodel_graph, "model_test")


def test_draw_graph_subgraph(model_instance):
    """Test change model settings
    
    It is hard to test the dot file because the order of
    the nodes is not garanteed.
    """

    model_instance.loop_parameter(params=["f"])
    dot_graph = draw_graph(
        model_instance.graph,
        "subgraph_test",
        show_detail=False,
        filename="test.gv",
        format="svg",
    )

    assert "subgraph cluster_f_loop_submodel" in dot_graph.source
