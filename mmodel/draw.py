import graphviz
import networkx as nx
from copy import deepcopy
from mmodel.doc import parse_description_graph

DEFAULT_SETTINGS = {
    "graph_attr": {
        "labelloc": "t",
        "labeljust": "l",
        "splines": "ortho",
        "ordering": "out",
    },
    "node_attr": {"shape": "box"},
}


def update_settings(label):
    """Update graphviz settings
    
    Creates a copy of the default dictionary
    and update the graph label in graph attribute
    """

    # copy() is shallow, does not copy the nested dict
    new_settings = deepcopy(DEFAULT_SETTINGS)
    new_settings["graph_attr"].update({"label": label})

    return new_settings


def draw_plain_graph(G, name, label):
    """Draw plain graph
    
    :param str name: name of the graph
    :param str label: title of the graph

    Plain graph contains the graph label (name + doc)
    Each node only shows the node name
    """

    settings = update_settings(label)
    dot_graph = graphviz.Digraph(name=name, **settings)

    for node in G.nodes:
        dot_graph.node(node)

    for u, v in G.edges:
        dot_graph.edge(u, v)

    return dot_graph


def draw_graph(G, name, label):
    """Draw detailed graph
    
    :param str name: name of the graph
    :param str label: title of the graph

    Plain graph contains the graph label (name + doc + input + output)
    Each node shows node label (name + signature + returns)

    Subgraph node shows the label and subgraph doc.
    """

    settings = update_settings(label)
    dot_graph = graphviz.Digraph(name=name, **settings)

    for node, ndict in G.nodes(data=True):
        rts = ", ".join(ndict["returns"])
        label = f"{node}\l\n{ndict['node_obj'].__name__}{ndict['signature']}\lreturn {rts}\l"
        dot_graph.node(node, label=label)

    for u, v, edict in G.edges(data=True):
        dot_graph.edge(u, v, xlabel=" ".join(edict["parameters"]))

    for node in nx.get_node_attributes(G, "has_subgraph").keys():

        subG = G.nodes[node]["node_obj"].G

        # use short docstring for subgraph
        label = parse_description_graph(subG._short_description())
        dot_sub = draw_graph(subG, name=f"cluster {node}", label=label)
        dot_graph.subgraph(dot_sub)

    return dot_graph

