"""Test draw_model function

draw_model returns a graphviz.DiGraph object, the tests consist of two parts
1. if draw model creates the correct dot string
"""

from mmodel.draw import draw_graph
from mmodel.model import Model
import pytest

dot_source = """digraph test {
graph [label="test\ntest object" labelloc=t ordering=out splines=ortho]
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



def test_draw_model_no_detail(mmodel_G):
    """Test the model without the node detail"""

    dot_graph = draw_graph(mmodel_G, name="test", show_detail=False)
    assert dot_graph.source.replace('\n', '').replace('\t', '') == dot_source.replace('\n', '')


def test_draw_model_detail(mmodel_G):
    """Test the model with full node and edge detail"""

    dot_graph = draw_graph(mmodel_G, name="test")
    assert "add\l\naddition(a, b=2)\lreturn c\l" in dot_graph.source


def test_draw_model_settings(mmodel_G):
    """Test change model settings"""

    dot_graph = draw_graph(
        mmodel_G,
        name="test",
        node_attr={"shape": "plaintext"},
        edge_attr={"label": "test"},
    )

    assert dot_graph.edge_attr == {"label": "test"}
    assert dot_graph.name == mmodel_G.name
    assert dot_graph.filename == f"{mmodel_G.name}.gv"
    assert "label=test" in dot_graph.source


@pytest.fixture
def model_instance(mmodel_G):
    """Create Model object for the test"""
    return Model(mmodel_G)


def test_draw_graph_subgraph(model_instance):
    """Test change model settings
 
    It is hard to test the dot file because the order of
    the nodes is not garanteed.
    """

    model_instance.loop_parameter(params=["f"])
    dot_graph = draw_graph(
        model_instance.G,
        show_detail=False,
        filename="test.gv",
        format="svg",
    )

    assert dot_graph.name == "test"
    assert "subgraph cluster_loop_f" in dot_graph.source
