"""Graph Operations"""
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
        with 'func_signature', 'return_params' defined for nodes
        and "interm_params" for edges.
        The args are a dictionary of inspected signature
    """

    parameters = {}
    for sig in nx.get_node_attributes(graph, "signature").values():
        for pname, param in sig.parameters.items():
            if pname in parameters:
                if param_sorter(parameters[pname]) >= param_sorter(param):
                    continue
            parameters.update({pname: param})

    for rts in nx.get_node_attributes(graph, "return_params").values():
        for rt in rts:
            parameters.pop(rt, None)  # if doesn't exist return None

    return inspect.Signature(sorted(parameters.values(), key=param_sorter))


def graph_returns(graph):
    """Obtain the return parameter of the graph

    The assumption is that all return parmaeter names are unique
    """

    returns = []

    for node in graph.nodes():
        if graph.out_degree(node) == 0:
            returns.extend(graph.nodes[node]["return_params"])

    return returns


def graph_layers(graph):
    """Determine the toplogical generation

    `nx.topological_generations` outputs a generator with each generation
    of node list. However, it does not carry the node attributes. The method
    outputs a list of node lists for each generation.

    return: topological layers of the graph, returns nested list
        each list in the list represent nodes in each layer.
        Each node is represented as a tuple (node, attrs)
    rtype: list
    """

    layers = []

    for layer in nx.topological_generations(graph):
        layers.append([(node, graph.nodes[node]) for node in layer])

    return layers


def param_counter(graph):
    """Count the number of times a parameter is used for graph execution

    This is done by counting the all function signature parameters

    return: dictionary with parameter_name: count pair
    rtype: dict
    """

    value_list = []
    for sig in nx.get_node_attributes(graph, "signature").values():
        value_list.extend(sig.parameters.keys())

    count = {}
    for value in value_list:
        count[value] = count.get(value, 0) + 1

    return count
