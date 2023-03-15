import graphviz
from copy import deepcopy

DEFAULT_SETTINGS = {
    "graph_attr": {
        "labelloc": "t",
        "labeljust": "l",
        "splines": "ortho",
        "ordering": "out",
    },
    "node_attr": {"shape": "box"},
}


def draw_graph(G, label, style, export=None, wrap_width=30):
    """Draw a detailed graph with options.

    :param str name: name of the graph
    :param str label: title of the graph
    :param str style: there are three valid styles, plain
        short and full. Each style corresponds to node-only,
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
                    nlabel = (
                        G.node_metadata(node, False, wrap_width).replace("\n", "\l")
                        + "\l"
                    )
                else:
                    nlabel = node

                dot_graph.node(node, label=nlabel)

        elif style == "full":
            for node, ndict in G.nodes(data=True):
                if "func" in ndict:
                    nlabel = (
                        G.node_metadata(node, True, wrap_width).replace("\n", "\l")
                        + "\l"
                    )
                else:
                    nlabel = node

                dot_graph.node(node, label=nlabel)

        for u, v, edict in G.edges(data=True):

            if "var" in edict:
                xlabel = edict["var"]
            else:
                xlabel = ""

            dot_graph.edge(u, v, xlabel=xlabel)

    if export:
        dot_graph.render(outfile=export)

    return dot_graph
