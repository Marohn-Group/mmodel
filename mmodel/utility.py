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


def model_signature(graph):
    """Obtain the signature from the model graph

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

    for returns in nx.get_node_attributes(graph, "returns").values():
        for rt in returns:
            parameters.pop(rt, None)  # if doesn't exist return None

    return inspect.Signature(sorted(parameters.values(), key=param_sorter))


def replace_signature(signature, replacement_dict):
    """Replace signature with a dictionary of (key, pair)

    The function is used to replace several input parameters with a object.
    The signature is the original signature.
    The dictionary key should be the replacement object, the values
    should be a list of the target parameters to be replaced.
    """

    params = dict(signature.parameters)
    for obj, target_list in replacement_dict.items():
        for target in target_list:
            del params[target]
        params[obj] = inspect.Parameter(obj, 1)

    return signature.replace(parameters=sorted(params.values(), key=param_sorter))


def model_returns(graph):
    """Obtain the return parameter from the model graph

    The assumption is that all return parmaeter names are unique
    """

    returns = []

    for node in graph.nodes():
        if graph.out_degree(node) == 0:
            returns.extend(graph.nodes[node]["returns"])

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


def param_counter(graph, add_returns):
    """Count the number of times a parameter is used for graph execution

    This is done by counting the all function signature parameters. For
    additional parameters (returns), simply add one to each count values.

    :param list add_params: added intermediate parameter to return for
        output.

    return: dictionary with parameter_name: count pair
    rtype: dict
    """

    value_list = []
    for sig in nx.get_node_attributes(graph, "sig").values():
        value_list.extend(sig.parameters.keys())

    # add the additional parameter to list
    value_list += add_returns

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


def modify_subgraph(
    model_graph, subgraph, subgraph_name, subgraph_obj, subgraph_returns=None
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

    # subgraph requires to have the returns attribute
    if subgraph_returns is None:
        try:
            subgraph_returns = subgraph_obj.returns
        except AttributeError:
            raise Exception("'subgraph_returns' not defined")

    graph.add_node_object(subgraph_name, obj=subgraph_obj, returns=subgraph_returns)
    # add the subgraph attribute to node
    graph.nodes[subgraph_name]["subgraph"] = subgraph

    return graph


def modify_node(model_graph, node, modifiers, node_returns=None):
    """Add modifiers to node

    The result is a new graph with node object modified
    """

    graph = model_graph.copy()
    obj = graph.nodes[node]["obj"]
    returns = node_returns or graph.nodes[node]["returns"]

    for mdf in modifiers:
        obj = mdf(obj)

    # update the loop value
    graph.add_node_object(node, obj=obj, returns=returns)

    return graph


def parse_input(signature, *args, **kwargs):
    """parse argument based on signature and input

    The default value is automatically filled.
    """

    values = signature.bind(*args, **kwargs)
    values.apply_defaults()
    return values.arguments


def is_node_attr_defined(graph, attr: str):
    """Check if all graph nodes have the target attribute defined
    
    Use ``set`` to ignore order. Returns true if all nodes have the target
    attribute
    """

    return set(nx.get_node_attributes(graph, attr).keys()) == set(graph.nodes)

def is_edge_attr_defined(graph, attr: str):
    """Check if all graph edges have the target attribute defined
    
    Use ``set`` to ignore order. Returns true if all nodes have the target
    attribute
    """

    return set(nx.get_edge_attributes(graph, attr).keys()) == set(graph.edges)
