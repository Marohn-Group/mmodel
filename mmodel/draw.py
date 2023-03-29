import graphviz
from copy import deepcopy
from mmodel.metadata import textwrap50, nodeformatter

DEFAULT_SETTINGS = {
    "graph_attr": {
        "labelloc": "t",
        "labeljust": "l",
        "splines": "ortho",
        "ordering": "out",
    },
    "node_attr": {"shape": "box"},
}


def draw_graph(
    G, label, style, export=None, formatter=nodeformatter, textwrapper=textwrap50
):
    """Draw a detailed graph with options.

    :param str name: name of the graph
    :param str label: title of the graph
    :param str style: there are three valid styles, plain
        short and verbose. Each style corresponds to node-only,
        function-only, and detailed note metadata graph
    :param str export: filename to export to
    """

    label = label.replace("\n", "\l") + "\l"
    settings = deepcopy(DEFAULT_SETTINGS)
    settings["graph_attr"].update({"label": label})

    dot_graph = graphviz.Digraph(name=G.name, **settings)

    if style == "plain":
        for node in G.nodes:
            dot_graph.node(node)

        for u, v in G.edges:
            dot_graph.edge(u, v)

    else:
        if style == "short":
            for node, ndict in G.nodes(data=True):
                if "func" in ndict:
                    metadata = G.node_metadata(node, False, formatter, textwrapper)
                    nlabel = metadata.replace("\n", "\l") + "\l"
                else:
                    nlabel = node

                dot_graph.node(node, label=nlabel)

        elif style == "verbose":
            for node, ndict in G.nodes(data=True):
                if "func" in ndict:
                    metadata = G.node_metadata(node, True, formatter, textwrapper)
                    nlabel = metadata.replace("\n", "\l") + "\l"
                else:
                    nlabel = node

                dot_graph.node(node, label=nlabel)

        else:
            raise Exception(
                f"Invalid style {repr(style)}: must be one of plain, short, or verbose."
            )

        for u, v, edict in G.edges(data=True):

            if "var" in edict:
                xlabel = edict["var"]
            else:
                xlabel = ""

            dot_graph.edge(u, v, xlabel=xlabel)

    if export:
        dot_graph.render(outfile=export)

    return dot_graph
