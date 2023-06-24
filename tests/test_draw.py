from mmodel.draw import draw_graph, replace_label
import networkx as nx
from textwrap import dedent
import pytest

def test_escape_label():
    """Test the label is escaped correctly."""

    label = "a\nb\\nc"
    assert replace_label(label) == r"a\lb\\nc\l"


DOT_PLAIN = r"""digraph test_graph {
graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
node [shape=box]
add
subtract
power
log
multiply
add -> subtract
add -> power
add -> log
subtract -> multiply
power -> multiply
}
"""

def test_draw_plain_model(mmodel_G):
    """Test the model without the node detail."""

    dot_graph = draw_graph(mmodel_G, label="test label", style="plain")
    assert dot_graph.source.replace("\t", "") == DOT_PLAIN


def test_draw_short_graph(mmodel_G):
    """Test the model with partial node and edge detail."""

    dot_graph = draw_graph(mmodel_G, label="test label", style="short")
    # test if the add function is included
    assert (
        r"add\l\laddition(a, constant=2)\lreturn: "
        r"c\lfunctype: callable\l\lAdd a constant to the value a."
        not in dot_graph.source
    )
    assert r"add\l\laddition(a, constant=2)\lreturn: c" in dot_graph.source


def test_draw_full_graph(mmodel_G):
    """Test the model with full node and edge detail."""

    dot_graph = draw_graph(mmodel_G, label="test label", style="verbose")
    # test if add function is included
    assert (
        r"add\l\laddition(a, constant=2)\lreturn: "
        r"c\lfunctype: callable\l\lAdd a constant to the value a." in dot_graph.source
    )

DOT_PARTIAL = r"""digraph test_graph {
graph [label="test label\l" labeljust=l labelloc=t ordering=out splines=ortho]
node [shape=box]
a [label=a]
b [label=b]
a -> b [xlabel=""]
}
"""

def test_draw_partial_graph():
    """Test draw detailed graph without node object information."""

    G = nx.DiGraph(name="test_graph")
    G.add_edge("a", "b")

    dot_graph_short = draw_graph(G, label="test label", style="short")
    dot_graph_full = draw_graph(G, label="test label", style="verbose")
    # assert dot_graph_short.source.replace("\t", "") == dedent(dot_source)
    assert dot_graph_short.source.replace("\t", "") == DOT_PARTIAL
    assert dot_graph_full.source.replace("\t", "") == DOT_PARTIAL


def test_draw_graph_export(mmodel_G, tmp_path):
    """Test draw graph can export and return a dot graph."""

    filename = tmp_path / "test_draw.dot"
    dot_graph = draw_graph(mmodel_G, label="test label", style="short", export=filename)

    # make sure it is not empty
    assert dot_graph.source is not None

    with open(filename, "r") as f:

        assert r"add\l\laddition(a, constant=2)\lreturn: c" in f.read()


def test_draw_raises_error(mmodel_G):
    """Test draw graph raises an error if the style is not valid."""

    with pytest.raises(
        Exception,
        match="Invalid style 'invalid': must be one of plain, short, or verbose.",
    ):
        draw_graph(mmodel_G, label="test label", style="invalid")
