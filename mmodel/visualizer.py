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
    lambda node, ndict: nodeformatter(ndict["node_obj"]),
    lambda u, v, edict: edict["var"],
)


# def draw_graph(
#     G, label, style, export=None, formatter=nodeformatter, textwrapper=textwrap50
# ):
#     """Draw a detailed graph with options.

#     :param str name: name of the graph
#     :param str label: title of the graph
#     :param str style: there are three valid styles, plain
#         short and verbose. Each style corresponds to node-only,
#         function-only, and detailed note metadata graph
#     :param str export: filename to export to
#     """

#     label = label.replace("\n", r"\l") + r"\l"
#     settings = deepcopy(DEFAULT_SETTINGS)
#     settings["graph_attr"].update({"label": label})

#     dot_graph = graphviz.Digraph(name=G.name, **settings)

#     if style == "plain":
#         for node in G.nodes:
#             dot_graph.node(node)

#         for u, v in G.edges:
#             dot_graph.edge(u, v)

#     else:
#         if style == "short":
#             for node, ndict in G.nodes(data=True):
#                 if "func" in ndict:
#                     metadata = G.node_metadata(node, False, formatter, textwrapper)
#                     nlabel = replace_label(metadata)
#                 else:
#                     nlabel = node

#                 dot_graph.node(node, label=nlabel)

#         elif style == "verbose":
#             for node, ndict in G.nodes(data=True):
#                 if "func" in ndict:
#                     metadata = G.node_metadata(node, True, formatter, textwrapper)
#                     nlabel = replace_label(metadata)
#                 else:
#                     nlabel = node

#                 dot_graph.node(node, label=nlabel)

#         else:
#             raise Exception(
#                 f"Invalid style {repr(style)}: must be one of plain, short, or verbose."
#             )

#         for u, v, edict in G.edges(data=True):
#             if "var" in edict:
#                 xlabel = edict["var"]
#             else:
#                 xlabel = ""

#             dot_graph.edge(u, v, xlabel=xlabel)

#     if export:
#         dot_graph.render(outfile=export)

#     return dot_graph
