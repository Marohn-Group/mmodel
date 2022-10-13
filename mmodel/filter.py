"""Filters that used to create subgraph"""
import networkx as nx


def subgraph_by_parameters(graph, parameters: list):
    """Construct subgraph based on parameters

    If a parent node is included, so are the child nodes.

    :return: subgraph view of the filtered graph
    """

    subgraph_nodes = []

    for node, sig in nx.get_node_attributes(graph, "sig").items():
        sig_params = sig.parameters
        for param in parameters:
            if param in sig_params:
                subgraph_nodes.append(node)
                subgraph_nodes.extend(nx.descendants(graph, node))

    return graph.subgraph(subgraph_nodes)


def subgraph_by_nodes(graph, nodes: list):
    """Construct subgraph based on nodes

    :return: subgraph view of the filtered graph
    """

    return graph.subgraph(nodes)


def subgraph_by_returns(graph, returns: list):
    """Construct subgraph based on node output

    :return: subgraph view of the filtered graph

    For mmodel graphs, returns from all the internal nodes are unique.
    Therefore the function only checks if function nodes overlap with
    the target return list. If a child node is included, so are the
    parent nodes.
    """

    subgraph_nodes = []

    for node, output in nx.get_node_attributes(graph, "output").items():

        if output in returns:

            subgraph_nodes.append(node)
            subgraph_nodes.extend(nx.ancestors(graph, node))

    return graph.subgraph(subgraph_nodes)
