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
    for sig in nx.get_node_attributes(graph, "signature").values():
        parameters.update(sig.parameters)

    for output in nx.get_node_attributes(graph, "output").values():
        parameters.pop(output, None)  # if doesn't exist return None

    return Signature(sorted(parameters.values(), key=param_sorter))


def modelgraph_returns(graph):
    """Obtain the return parameter from the model graph.

    The assumption is that all return parameter names are unique.

    :returns: list of variable names based on note outputs
    :rtype: list
    """

    returns_list = []
    for node, output in nx.get_node_attributes(graph, "output").items():
        if graph.out_degree(node) == 0 and output is not None:
            returns_list.append(output)
    returns_list.sort()
    return returns_list


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


def replace_subgraph(graph, subgraph, subgraph_node):
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
                new_edges.append((parent, subgraph_node.name))
        for child in graph.successors(node):
            if child not in subgraph:
                new_edges.append((subgraph_node.name, child))

    graph.remove_nodes_from(subgraph.nodes)
    # remove unique edges
    graph.add_edges_from(set(new_edges))
    graph.set_node_object(subgraph_node)

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
    for sig in nx.get_node_attributes(graph, "signature").values():
        for key, param in sig.parameters.items():
            if param.default is param.empty:
                value_list.append(key)

    # add the additional parameter to list
    value_list += returns

    count = {}
    for value in value_list:
        count[value] = count.get(value, 0) + 1

    return count


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


def construction_dict(obj, property_list=None, exclude_list=None):
    """Return a dictionary that contains object construction parameters.

    The property list and exclude list need to be manually input.
    The exclude list is used for object attributes that are not
    part of the object construction, but public attributes.
    The object attribute omits private ('_') values, but includes all
    public attributes that are not in the exclude list.
    """
    property_list = property_list or []
    exclude_list = exclude_list or []

    ppt_dict = {key: getattr(obj, key) for key in property_list}
    attr_dict = {
        key: value
        for key, value in obj.__dict__.items()
        if not key.startswith("_") and key not in exclude_list
    }
    return {**ppt_dict, **attr_dict}


def modify_func(func, modifiers):
    """Apply modifiers to node_func."""

    for mod in modifiers:
        func = mod(func)
    return func


def parse_functype(func):
    """Parse function type.

    For functions that are not a standard callable, returns
    the module name, such as numpy.ufunc.
    """

    tp = type(func)

    if tp.__module__ == "builtins":
        return tp.__qualname__

    else:
        return f"{tp.__module__}.{tp.__qualname__}"
