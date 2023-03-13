"""Filters that used to create subgraph"""
import networkx as nx


def subnodes_by_inputs(graph, inputs: list):
    """Obtain list of subgraph nodes based on node inputs

    If a parent node is included, so are the child nodes.

    :return: list of node names
    """

    subgraph_nodes = []

    for node, sig in nx.get_node_attributes(graph, "sig").items():
        sig_params = sig.parameters
        for param in inputs:
            if param in sig_params:
                subgraph_nodes.append(node)
                subgraph_nodes.extend(nx.descendants(graph, node))
    
    return subgraph_nodes


def subnodes_by_outputs(graph, outputs: list):
    """Obtain list of subgraph nodes based on node outputs

    :return: list of node names

    For mmodel graphs, outputs from all the internal nodes are unique.
    Therefore the function only checks if function nodes overlap with
    the target return list. If a child node is included, so are the
    parent nodes.
    """

    subgraph_nodes = []
    for node, output in nx.get_node_attributes(graph, "output").items():

        if output in outputs:

            subgraph_nodes.append(node)
            subgraph_nodes.extend(nx.ancestors(graph, node))

    return subgraph_nodes
