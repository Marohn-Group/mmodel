import networkx as nx
from functools import wraps
import itertools
from inspect import signature, Parameter, Signature


def subgraph_from_params(graph, parameters):
    """Construct subgraph based on parameters

    :param list params: target input paramaters to be included in
        the subgraph

    :return: a copy of the subgraph
    """

    subgraph_nodes = []

    for node, sig in nx.get_node_attributes(graph, "signature").items():
        sig_params = sig.parameters
        for param in parameters:
            if param in sig_params:
                subgraph_nodes.append(node)
                subgraph_nodes.extend(nx.descendants(graph, node))

    return graph.subgraph(subgraph_nodes)


def redirect_edges(
    graph, subgraph, subgraph_node, node_obj, return_params, loop_params
):
    """Redirect graph based on subgraph

    Find all parent node that is not in subgraph but have child node
    in subgraph. (All child node of subgraph nodes are in the subgraph).
    The edge attribute is passed down to the new edge

    :param str node: node name for the subgraph node
    :param callable node_obj: looped model object
    :param list loop_params: loop parameter list
    """
    subgraph = subgraph.copy()
    graph = graph.copy()
    visited_parents = []
    new_edges = []
    for node in subgraph.nodes():
        for parent in graph.predecessors(node):
            if parent not in subgraph and parent not in visited_parents:
                visited_parents.append(parent)
                edge_attr = graph[parent][node]
                new_edges.append([parent, subgraph_node, edge_attr])

    graph.remove_nodes_from(subgraph.nodes)

    graph.add_node(
        subgraph_node,
        node_obj=node_obj,
        return_params=return_params,
        loop_params=loop_params,
        has_subgraph=True,
        has_loop=True
    )
    graph.add_edges_from(new_edges)

    return graph


def basic_loop(func, params):
    """Basic loop wrapper, iterates the values from loop

    The basic loop only allows to loop one parameter

    :param list params: list of the parameter to loop
        only one parameter is allowed

    :return: function that loops designed parameter
    :rtype: func

    TODO
        test speed of signature modification
        consider not allow multiple loop parameters (but maybe pairwise is allowed?)
    """

    if len(params) != 1:
        raise Exception('basic_loop accept one parameter at a time')
    param = params[0]
    # reset the default to a list
    sig_param = dict(signature(func).parameters)
    _param = sig_param[param]
    if _param.default != Parameter.empty:
        sig_param[param] = Parameter(_param.name, _param.kind, default=[_param.default])
    sig = Signature(sig_param.values())

    @wraps(func)
    def loop_wrapper(*args, **kwargs):

        # the following check is unnecessary, consider remove them
        values = sig.bind(*args, **kwargs)
        values.apply_defaults()
        value_dict = values.arguments

        loop_values = value_dict.pop(param)
        result = [func(**value_dict, **{param: value}) for value in loop_values]

        return result

    # modify the signature
    loop_wrapper.__signature__ = sig

    return loop_wrapper
