import graphviz
from copy import deepcopy
from mmodel.metadata import modelformatter, nodeformatter
import re
from dataclasses import dataclass
import networkx as nx

default_graph_settings = {
    "graph_attr": {
        "labelloc": "t",
        "labeljust": "l",
        "splines": "ortho",
        "ordering": "out",
    },
    "node_attr": {"shape": "box"},
}


def format_label(label):
    """Format label for graphviz.

    The function replaces newlines with the graphviz left aligned line break.
    However if the ``\n`` is escaped, change it to ``\\\\n``.
    """
    return re.sub(r"(?<!\\)\n", r"\\l", label).replace("\\n", "\\\\n") + r"\l"


class Visualizer:
    """Visualizer class for drawing networkx graph."""

    def __init__(
        self,
        format_node,
        format_edge,
        graph_settings=default_graph_settings,
    ):
        self.graph_settings = graph_settings
        self.format_node = staticmethod(format_node)
        self.format_edge = staticmethod(format_edge)

    def __call__(self, G, label=None, outfile=None):
        """Draw the graph based on the object."""

        label = label.replace("\n", r"\l") + r"\l"

        settings = deepcopy(self.graph_settings)
        settings["graph_attr"].update({"label": label})

        dot_graph = graphviz.Digraph(name=G.name, **settings)

        for node, ndict in G.nodes(data=True):
            node_str = self.format_node(node, ndict)
            nlabel = format_label(node_str)
            dot_graph.node(node, label=nlabel)

        for u, v, edict in G.edges(data=True):
            edge_str = self.format_edge(u, v, edict)
            xlabel = format_label(edge_str)
            dot_graph.edge(u, v, xlabel=xlabel)

        if outfile:
            dot_graph.render(outfile=outfile)

        return dot_graph


plain_visualizer = Visualizer(lambda node, ndict: node, lambda u, v, edict: "")
visualizer = Visualizer(
    lambda node, ndict: nodeformatter(ndict["node_object"]),
    lambda u, v, edict: edict["output"],
)
