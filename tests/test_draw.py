from mmodel.draw import draw_graph
import networkx as nx
from textwrap import dedent


def test_draw_plain_model(mmodel_G):
    """Test the model without the node detail"""

    dot_source = """\
    digraph test_graph {
    graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
    node [shape=box]
    add
    subtract
    poly
    log
    multiply
    add -> subtract
    add -> poly
    add -> log
    subtract -> multiply
    poly -> multiply
    }
    """

    dot_graph = draw_graph(mmodel_G, label="test label", style="plain")
    assert dot_graph.source.replace("\t", "") == dedent(dot_source)


def test_draw_short_graph(mmodel_G):
    """Test the model with partial node and edge detail"""

    dot_graph = draw_graph(mmodel_G, label="test label", style="short")
    # test if add function is included
    assert (
        "add\l\laddition(a, factor=2)\lreturn: "
        "c\lfunctype: callable\l\laddition operation" not in dot_graph.source
    )
    assert "add\l\laddition(a, factor=2)\lreturn: c" in dot_graph.source


def test_draw_full_graph(mmodel_G):
    """Test the model with full node and edge detail"""

    dot_graph = draw_graph(mmodel_G, label="test label", style="full")
    # test if add function is included
    assert (
        "add\l\laddition(a, factor=2)\lreturn: "
        "c\lfunctype: callable\l\laddition operation" in dot_graph.source
    )


def test_draw_partial_graph():
    """Test draw detailed graph without node object information"""

    dot_source = """\
    digraph test_graph {
    graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
    node [shape=box]
    a [label=a]
    b [label=b]
    a -> b [xlabel=""]
    }
    """

    G = nx.DiGraph(name="test_graph")
    G.add_edge("a", "b")

    dot_graph = draw_graph(G, label="test label", style="short")

    assert dot_graph.source.replace("\t", "") == dedent(dot_source)


def test_draw_graph_export(mmodel_G, tmp_path):
    """Test draw graph can export and return a dot graph"""

    filename = tmp_path / "test_draw.dot"
    dot_graph = draw_graph(mmodel_G, label="test label", style="short", export=filename)

    # make sure it is not empty
    assert dot_graph.source is not None

    with open(filename, "r") as f:

        assert "add\l\laddition(a, factor=2)\lreturn: c" in f.read()
