import inspect
import networkx as nx


def param_sorter(parameter):
    """Sorter for argument parameter

    The values in the tuple are compared in sequential order
    1. Order by parameter kind
    2. Default parameter rank at the end of its kind
    3. Alphabetical order

    :param inspect.Parameter parameter: parameter object
    :rtype: (bool, parameter.name, parameter.kind)
    """

    if parameter.default is not parameter.empty:
        return parameter.kind, True, parameter.name
    else:
        return parameter.kind, False, parameter.name


def graph_signature(graph):
    """Obtain the signature of the graph

    TODO
        add parameter checking method
        check returns and also the edge parameter

    :param DiGraph graph: networkx.Digraph() object,
        with 'func_signature', 'returns' defined for nodes
        and "parameters" for edges.
        The args are a dictionary of inspected signature
    """

    parameters = {}
    for sig in nx.get_node_attributes(graph, "sig").values():
        for pname, param in sig.parameters.items():
            if pname in parameters:
                if param_sorter(parameters[pname]) >= param_sorter(param):
                    continue
            parameters.update({pname: param})

    for rts in nx.get_node_attributes(graph, "rts").values():
        for rt in rts:
            parameters.pop(rt, None)  # if doesn't exist return None

    return inspect.Signature(sorted(parameters.values(), key=param_sorter))


def replace_signature(signature, replacement_dict):
    """Replace signature with a dictionary of (key, pair)

    The function is used to replace several input parameters with a object.
    The signature is the original sigature.
    The dictionary key should be the replacement object, the values
    should be a list of the target parameters to be replaced.
    """

    params = dict(signature.parameters)
    for obj, target_list in replacement_dict.items():
        for target in target_list:
            del params[target]
        params[obj] = inspect.Parameter(obj, 1)

    return signature.replace(parameters=sorted(params.values(), key=param_sorter))


def graph_returns(graph):
    """Obtain the return parameter of the graph

    The assumption is that all return parmaeter names are unique
    """

    returns = []

    for node in graph.nodes():
        if graph.out_degree(node) == 0:
            returns.extend(graph.nodes[node]["rts"])

    returns.sort()
    return returns


def graph_topological_sort(graph):
    """Determine the toplogical order

    `nx.topological_generations` outputs a generator with each generation
    of node list. However, it does not carry the node attributes. The method
    outputs a list of node lists for each generation.

    :return: topological order of the graph, returns a list of nodes and its
        attribute
    :rtype: list

    """

    topological_order = []

    for node in nx.topological_sort(graph):
        topological_order.append((node, graph.nodes[node]))

    return topological_order


def param_counter(graph):
    """Count the number of times a parameter is used for graph execution

    This is done by counting the all function signature parameters

    return: dictionary with parameter_name: count pair
    rtype: dict
    """

    value_list = []
    for sig in nx.get_node_attributes(graph, "sig").values():
        value_list.extend(sig.parameters.keys())

    count = {}
    for value in value_list:
        count[value] = count.get(value, 0) + 1

    return count


# def loop_signature(signature, parameters):
#     """Change parameter default from scalar to list"""

#     # reset the default to a list
#     sig_param = dict(signature.parameters)
#     for parameter in parameters:
#         _param = sig_param[parameter]
#         if _param.default != inspect.Parameter.empty:
#             sig_param[parameter] = inspect.Parameter(
#                 _param.name, _param.kind, default=[_param.default]
#             )
#     return inspect.Signature(sig_param.values())


def subgraph_by_parameters(graph, parameters):
    """Construct subgraph based on parameters

    The function is specifically used for loops. In the looping,
    the subgraph needs to be a complete version.
    :param list params: target input paramaters to be included in
        the subgraph

    :return: a copy of the subgraph
    """

    subgraph_nodes = []

    for node, sig in nx.get_node_attributes(graph, "sig").items():
        sig_params = sig.parameters
        for param in parameters:
            if param in sig_params:
                subgraph_nodes.append(node)
                subgraph_nodes.extend(nx.descendants(graph, node))

    return graph.subgraph(subgraph_nodes)

def subgraph_by_nodes(graph, nodes):
    """Construct subgraph based on nodes"""

    return graph.subgraph(nodes)


def modify_subgraph(
    model_graph, subgraph, subgraph_name, subgraph_obj, subgraph_returns
):
    """Redirect graph based on subgraph

    Find all parent node that is not in subgraph but have child node
    in subgraph. (All child node of subgraph nodes are in the subgraph).
    The edge attribute is passed down to the new edge

    :param graph model_graph: model_graph to modify
    :param graph subgraph: subgraph that is being replaced by a node
    :param str subgraph_name: name of the subgraph
    """

    graph = model_graph.copy()
    subgraph = subgraph.copy()
    subgraph.name = subgraph_name

    new_edges = []
    for node in subgraph.nodes():
        for parent in graph.predecessors(node):
            if parent not in subgraph:
                new_edges.append((parent, subgraph_name))
        for child in graph.successors(node):
            if child not in subgraph:
                new_edges.append((subgraph_name, child))

    graph.remove_nodes_from(subgraph.nodes)
    # remove unique edges
    graph.add_edges_from(set(new_edges))

    graph.update_node_object(
        subgraph_name,
        obj=subgraph_obj,
        rts=subgraph_returns,
        subgraph=subgraph,
    )

    return graph

def modify_node(model_graph, node,  modifiers, node_returns=None):
    """Add modifiers to node
    
    The result is a new graph with node object modified
    """

    graph = model_graph.copy()
    obj = graph.nodes[node]['obj']
    rts = node_returns or graph.nodes[node]['rts']

    for mdf in modifiers:
        obj = mdf(obj)

    # update the loop value
    graph.update_node_object(node, obj=obj, rts=rts)

    return graph



def parse_input(signature, *args, **kwargs):
    """parse argument based on signature and input"""

    values = signature.bind(*args, **kwargs)
    values.apply_defaults()
    return values.arguments

