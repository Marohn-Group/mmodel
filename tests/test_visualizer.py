from mmodel.visualizer import format_label, plain_visualizer, visualizer
import networkx as nx
from textwrap import dedent
import pytest


def test_escape_label():
    """Test the label is escaped correctly."""

    label = "a\nb\\nc"
    assert format_label(label) == r"a\lb\\nc\l"


DOT_PLAIN = r"""digraph test_graph {
graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
node [shape=box]
add [label="add\l"]
subtract [label="subtract\l"]
power [label="power\l"]
log [label="log\l"]
multiply [label="multiply\l"]
add -> subtract [xlabel="\l"]
add -> power [xlabel="\l"]
add -> log [xlabel="\l"]
subtract -> multiply [xlabel="\l"]
power -> multiply [xlabel="\l"]
}
"""


def test_draw_plain_graph_default(mmodel_G):
    """Test the graph without the node detail."""

    dot_graph = plain_visualizer(mmodel_G, label="test label")
    assert dot_graph.source.replace("\t", "") == DOT_PLAIN


def test_draw_default_viz(mmodel_G):
    """Test the default_viz with full node and edge detail for model."""

    dot_graph = visualizer(mmodel_G, label="test label")
    # test if add function is included
    assert (
        r"add\l\laddition(a)\lreturn: "
        r"c\lfunctype: function\l\lAdd a constant to the value a." in dot_graph.source
    )


DOT_PARTIAL = r"""digraph test_graph {
graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
node [shape=box]
a [label="a\l"]
b [label="b\l"]
a -> b [xlabel="\l"]
}
"""


def test_draw_partial_graph():
    """Test draw partial graph without node object information."""

    G = nx.DiGraph(name="test_graph")
    G.add_edge("a", "b")

    dot_graph_plain = plain_visualizer(G, label="test label")

    # assert dot_graph_short.source.replace("\t", "") == dedent(dot_source)
    assert dot_graph_plain.source.replace("\t", "") == DOT_PARTIAL


def test_draw_graph_export(mmodel_G, tmp_path):
    """Test draw graph can export and return a dot graph."""

    filename = tmp_path / "test_draw.dot"
    dot_graph = visualizer(mmodel_G, label="test label", outfile=filename)

    # make sure it is not empty
    assert dot_graph.source is not None

    with open(filename, "r") as f:
        assert r"add\l\laddition(a)\lreturn: c" in f.read()
