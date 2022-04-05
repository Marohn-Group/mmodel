"""Test draw_model function

draw_model returns a graphviz.DiGraph object, the tests consist of two parts
1. if draw model creates the correct dot string
"""

from mmodel.draw import draw_graph, draw_plain_graph, update_settings, DEFAULT_SETTINGS
from mmodel.model import Model


dot_source = """digraph test {
graph [label="test label" labeljust=l labelloc=t ordering=out splines=ortho]
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


def test_update_settings():
    """Test the update_settings function"""

    setttings = update_settings("test label")
    assert setttings["graph_attr"]["label"] == "test label"

    # check default is deepcopied
    assert not "label" in DEFAULT_SETTINGS["graph_attr"]


def test_draw_plain_model(mmodel_G):
    """Test the model without the node detail"""

    dot_graph = draw_plain_graph(mmodel_G, name="test", label="test label")
    assert dot_graph.source.replace("\n", "").replace("\t", "") == dot_source.replace(
        "\n", ""
    )


def test_draw_graph(mmodel_G):
    """Test the model with full node and edge detail"""

    dot_graph = draw_graph(mmodel_G, name="test", label="test label")
    # test if add function is included
    assert "add\l\naddition(a, b=2)\lreturn c\l" in dot_graph.source


def test_graph_draw_graph(mmodel_G):
    """Test graph draw_model

    Here test if the label value are plotted correctly
    """
    graph = mmodel_G.draw_graph()
    assert graph.name == "test"
    assert 'label="test: test object\l"' in graph.source

    detail_graph = mmodel_G.draw_graph(show_detail=True)
    assert "input parameters: (a, d, f, b=2)\l" in detail_graph.source
    assert detail_graph.name == "test"
    assert "return parameters: k, m" in detail_graph.source


def test_model_draw_graph(mmodel_G):
    """Test graph model_model

    Here test if the label value are plotted correctly
    """
    model = Model(mmodel_G)
    graph = model.draw_graph()
    assert graph.name == "test model"
    assert 'label="test model: test object\lclass: Model\l"' in graph.source

    detail_graph = model.draw_graph(show_detail=True)
    assert detail_graph.name == "test model"
    assert "class: Model\l" in detail_graph.source
    assert "signature: (a, d, f, b=2)\l" in detail_graph.source
    assert "returns: k, m\l" in detail_graph.source


def test_model_loop_draw_graph(mmodel_G):
    """Test graph model_model with loop

    Here test if the label value are plotted correctly
    """
    model = Model(mmodel_G)
    model.loop_parameter(params=["f"])

    detail_graph = model.draw_graph(show_detail=True)

    assert detail_graph.name == "test model"
    assert "class: Model\l" in detail_graph.source
    assert "signature: (a, d, f, b=2)\l" in detail_graph.source
    assert "returns: m, k\l" in detail_graph.source

    # subgraph content
    assert 'subgraph "cluster loop f"' in detail_graph.source
    assert 'label="loop f: basic_loop method\l"' in detail_graph.source
