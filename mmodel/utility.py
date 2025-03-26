from inspect import Signature, Parameter, signature
import networkx as nx


def modelgraph_signature(graph):
    """Obtain the signature from the model graph.

    :param DiGraph graph: ``networkx.Digraph`` object,
        with "signature" and "output" defined for nodes
        and "parameters" for edges.
        The args are a dictionary of inspected signatures.
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


def check_model_returns(graph, returns):
    """Check if the user defined returns are valid.

    The function is used by the model, where only returns
    with elements are passed.

    :param list returns: returns to check.
    :rtype: list
    """

    ouputs = list(nx.get_node_attributes(graph, "output").values())
    inputs = list(modelgraph_signature(graph).parameters.keys())
    graph_returns = ouputs + inputs

    for return_var in returns:
        if return_var not in graph_returns:
            raise ValueError(
                f"user defined return {repr(return_var)} not in the graph."
            )
    return True


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

    :return: topological order of the graph. Returns a list of nodes and their
        attributes.
    :rtype: list

    """

    topological_order = []

    for node in nx.topological_sort(graph):
        topological_order.append((node, graph.nodes[node]))

    return topological_order


def replace_subgraph(graph, subgraph, subgraph_node):
    """Replace subgraph with a node.

    Find all parent nodes, not in the subgraph, but child nodes in the
    subgraph. (All child nodes of subgraph nodes are in the subgraph).
    The edge attribute is passed down to the new edge. Here, a new graph is
    created by deep copying the original graph.

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
    graph.add_node_object(subgraph_node)
    graph.add_edges_from(set(new_edges))

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


def is_node_attr_defined(graph, attr: str):
    """Check if all graph nodes have the attribute defined.

    :param str attr: attribute string.

    Raise an exception if the attribute is undefined.
    """

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
            f"invalid {graph_str}: attribute "
            f"{repr(attr)} is not defined for node(s) {node_list}."
        )

    return True


def is_edge_attr_defined(graph, attr: str):
    """Check if all graph edges have the target attribute defined.

    Raise an exception if the attribute is undefined.
    """

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
            f"invalid {graph_str}: attribute {repr(attr)}"
            f" is not defined for edge(s) {edge_list}."
        )

    return True


def is_node_output_unique(graph):
    """Check if all node output attribute are unique.

    The restriction is added in version 0.8.1. The reason
    being that several methods including the subgraph filter
    and the intermediate returns relies on the unique output.

    Here we allow None values to be duplicated.
    The algorithm is simply to start a new list for comparison.
    Raise an exception if the node attribute values are not unique.
    """

    if graph.name:
        graph_str = f"graph ({graph.name})"
    else:
        graph_str = "graph"

    compare_list = []
    for node, output in nx.get_node_attributes(graph, "output").items():
        if output is not None:
            if output in compare_list:
                raise Exception(
                    f"invalid {graph_str}: duplicated output {repr(output)}"
                    f" for node {repr(node)}."
                )
            compare_list.append(output)

    return True


def modify_func(func, modifiers):
    """Apply modifiers to function."""

    for mod in modifiers:
        func = mod(func)
    return func


def parse_functype(func):
    """Parse function type.

    For functions that are not a standard callable, returns
    the module name, such as ``numpy.ufunc``.
    """

    tp = type(func)

    if tp.__module__ == "builtins":
        return tp.__qualname__

    else:
        return f"{tp.__module__}.{tp.__qualname__}"


class EditMixin:
    """Mixin class that records the parameters that used in constructor.

    For classes that allows the edit method to create a new instance,
    we keep track of the constructor parameter with the __new__ method.
    Some of the constructor parameters might not be saved as attributes
    or attributes of the same name, therefore the values are stored as well.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new instance of the model.

        Here we modify the __new__ method to store the constructor parameters
        in the instance. We combine the __init__ signature, and the
        applied keyword arguments.
        """
        # remove self; **kwargs is still in the signature but that's okay
        init_keys = list(signature(cls.__init__).parameters.keys())[1:]
        init_dict = dict(zip(init_keys, args))
        init_dict.update(kwargs)

        instance = super().__new__(cls)
        instance._init_dict = init_dict
        return instance

    @property
    def edit_dict(self):
        """Get the current attributes based on init_dict.

        Some parameters are defined as properties to avoid the same reference.
        The method here updates the current values of the attributes.
        """
        return {k: getattr(self, k, self._init_dict[k]) for k in self._init_dict}


class ReprMixin:

    def __repr__(self):
        """Return the representation of the object.

        The representation outputs the class name and the instance name.
        The class requires to have a "name" attribute.
        """

        name = getattr(self, "name", None)
        name_str = f" {repr(name)}" if name else ""

        return f"<{type(self).__module__}.{self.__class__.__name__}{name_str}>"
