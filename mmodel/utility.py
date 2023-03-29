from inspect import Signature, Parameter
import networkx as nx

# graph properties
def modelgraph_signature(graph):
    """Obtain the signature from the model graph.

    :param DiGraph graph: networkx.Digraph() object,
        with 'signature', and 'output' defined for nodes
        and "parameters" for edges.
        The args are a dictionary of inspected signature.
    """

    parameters = {}
    for sig in nx.get_node_attributes(graph, "sig").values():
        for pname, param in sig.parameters.items():
            # remove the default values
            if param.default is param.empty and param not in parameters:
                parameters.update({pname: param})

    for output in nx.get_node_attributes(graph, "output").values():
        parameters.pop(output, None)  # if doesn't exist return None

    return Signature(sorted(parameters.values(), key=param_sorter))


def modelgraph_returns(graph):
    """Obtain the return parameter from the model graph.

    The assumption is that all return parameter names are unique.
    The function checks all returns values and all intermediate values (edge values)

    :returns: list of variable names based on note outputs
    :rtype: list
    """

    returns = []
    intermediate = []

    for node in graph.nodes():
        if graph.nodes[node]["output"]:  # skip None
            returns.append(graph.nodes[node]["output"])
    for edge in graph.edges():
        intermediate.append(graph.edges[edge]["var"])

    final_returns = list(set(returns) - set(intermediate))
    final_returns.sort()
    return final_returns


def param_sorter(parameter):
    """Sorter for argument parameter.

    The values in the tuple are compared in sequential order:
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


def replace_signature(signature, replacement_dict):
    """Replace signature with a dictionary of (key, pair).

    The function is used to replace several input parameters with an object.
    The signature is the original signature. The dictionary key should be the
    replacement object, and the values should be a list of the target
    parameters to be replaced. The replacement allows unused parameters, they
    are skipped.
    """

    params = dict(signature.parameters)
    for func, target_list in replacement_dict.items():
        for target in target_list:
            # del params[target]
            params.pop(target, None)
        params[func] = Parameter(func, 1)

    return signature.replace(parameters=sorted(params.values(), key=param_sorter))


def graph_topological_sort(graph):
    """Determine the topological order.

    `nx.topological_generations` outputs a generator with each node list generation.
    However, it does not carry the node attributes. The method
    outputs a list of nodes for each generation.

    :return: topological order of the graph. Returns a list of nodes and its
        attribute.
    :rtype: list

    """

    topological_order = []

    for node in nx.topological_sort(graph):
        topological_order.append((node, graph.nodes[node]))

    return topological_order


def replace_subgraph(
    graph, subgraph, name, func, output=None, inputs=None, modifiers=None
):
    """Replace subgraph with a node.

    Find all parent nodes, not in the subgraph but child nodes in the
    subgraph. (All child nodes of subgraph nodes are in the subgraph).
    The edge attribute is passed down to the new edge. Here a new graph is
    created by deep copy the original graph.

    :param graph model_graph: model_graph to modify.
    :param graph subgraph: subgraph that is being replaced by a node
        subgraph is a view of the original graph.
    :param str subgraph_name: name of the subgraph.
    :param str output: output parameter name.
    """

    graph = graph.deepcopy()

    new_edges = []
    for node in subgraph.nodes():
        for parent in graph.predecessors(node):
            if parent not in subgraph:
                new_edges.append((parent, name))
        for child in graph.successors(node):
            if child not in subgraph:
                new_edges.append((name, child))

    graph.remove_nodes_from(subgraph.nodes)
    # remove unique edges
    graph.add_edges_from(set(new_edges))

    graph.set_node_object(
        name, func=func, output=output, inputs=inputs, modifiers=modifiers
    )

    return graph


def modify_node(
    graph, node, func=None, output=None, inputs=None, modifiers=None, inplace=False
):
    """Modify node.

    The result is a new graph with the node object modified.
    :param str output: change the output of the node. If the node is not
        terminal, the output should not be changed.
    :param bool inplace: if True, the original graph is modified.

    .. Note::

        If the original node has output, the node cannot be modified to None.
        If the original node has inputs, the modification cannot remove the
        original input (set to [] does not change anything).

        For the above two cases, a copy of the graph should be created and run
        ``set_node_object`` again to reset the node object.

    """
    if not inplace:
        graph = graph.deepcopy()

    func = func or graph.nodes[node]["_func"]
    modifiers = modifiers or graph.nodes[node]["modifiers"]
    output = output or graph.nodes[node]["output"]
    graph.set_node_object(
        node, func=func, output=output, inputs=inputs, modifiers=modifiers
    )

    return graph


def parse_parameters(parameters):
    """Parse a list of parameters to signatures

    :param list parameters: Parameters to parse. The element can either be a string
        as the parameter name or a tuple/list as (parameter, default).
    :return: parameter order and signature.
    """

    param_order = []  # parameters in the correct order
    sig_list = []  # signature values
    sig_df_list = []  # default values
    defultargs = {}  # default arguments dictionary
    for var in parameters:
        if isinstance(var, tuple) or isinstance(var, list):
            var_name, default_value = var
            param_order.append(var_name)
            sig_df_list.append(Parameter(var_name, 1, default=default_value))
            defultargs[var_name] = default_value
        else:
            param_order.append(var)
            sig_list.append(Parameter(var, 1))

    sig = Signature(sig_list + sig_df_list)  # the default values are ordered next

    return sig, param_order, defultargs


def param_counter(graph, returns):
    """Count the number of times a parameter is used for graph execution.

    Count all function signature parameters. For extra returns,
    add one to each count value.

    :param list returns: method returns (include extra returns)
    :return: dictionary with parameter_name: count pair
    :rtype: dict
    """

    value_list = []
    for sig in nx.get_node_attributes(graph, "sig").values():
        for key, param in sig.parameters.items():

            if param.default is param.empty:
                value_list.append(key)

    # add the additional parameter to list
    value_list += returns

    count = {}
    for value in value_list:
        count[value] = count.get(value, 0) + 1

    return count


def parse_input(signature, *args, **kwargs):
    """parse argument based on signature and input.

    The default value is automatically filled.
    """

    values = signature.bind(*args, **kwargs)
    values.apply_defaults()
    return values.arguments


def is_node_attr_defined(graph, attr: str, attr_name: str = None):
    """Check if all graph nodes have the attribute defined.

    :param str attr: attribute string.
    :param str attr_name: the detailed name of the attribute.

    Raise an exception if the attribute is undefined.
    """
    attr_name = attr_name or attr

    if graph.name:
        graph_str = f"graph ({graph.name})"
    else:
        graph_str = "graph"

    node_list = []
    for node, node_attr in graph.nodes.data():
        if attr not in node_attr:
            node_list.append(node)

    if node_list:
        raise Exception(
            f"invalid {graph_str}: {attr_name} "
            f"{repr(attr)} is not defined for node(s) {node_list}."
        )

    return True


def is_edge_attr_defined(graph, attr: str, attr_name: str = None):
    """Check if all graph edges have the target attribute defined.

    Raise an exception if the attribute is undefined.
    """
    attr_name = attr_name or attr

    if graph.name:
        graph_str = f"graph ({graph.name})"
    else:
        graph_str = "graph"

    edge_list = []
    for u, v, edge_attr in graph.edges.data():
        if attr not in edge_attr:
            edge_list.append((u, v))
    if edge_list:
        raise Exception(
            f"invalid {graph_str}: {attr_name} {repr(attr)}"
            f" is not defined for edge(s) {edge_list}."
        )

    return True
