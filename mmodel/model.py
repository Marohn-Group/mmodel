import inspect
from mmodel.utility import parse_input, is_node_attr_defined, is_edge_attr_defined
import networkx as nx


class Model:
    """Create model executable

    :param object graph: ModelGraph instance (digraph)
    :param class handler: Handler class that handles model execution
        Handler class can only take two parameter arguments, graph and
        additional_returns. If additional parameters are required,
        use partial_handler to define updated Handler class.
    :param list modifiers: modifiers used for the whole graph model executable.
        Optional, defaults to a empty list.
    :param list add_returns: additional parameters to return. The parameter is
        used for retrieving intermediate values of the graph model.
        Optional, defaults to a empty list.
    """

    def __init__(
        self, graph, handler, modifiers: list = [], additional_returns: list = []
    ):

        assert self.is_graph_valid(graph)

        self.__name__ = f"{graph.name} model"

        # store only the copy of the graph, note this is not the same copy
        # used by the handler
        # modify self._graph does not change the model itself
        self._graph = graph.copy()
        self._modifiers = modifiers
        self._handler = handler

        executor = handler(graph, additional_returns)
        self._handler_info = getattr(executor, "info", self._handler.__name__)

        for mdf in modifiers:
            executor = mdf(executor)

        self.__signature__ = executor.__signature__
        self.returns = executor.returns
        self.executor = executor

    def __call__(self, *args, **kwargs):

        # process input
        data_input = parse_input(self.__signature__, *args, **kwargs)

        return self.executor(**data_input)

    def __str__(self):
        """Output callable information"""

        sig_list = [str(param) for param in self.__signature__.parameters.values()]

        mod_str_list = [getattr(mod, "info", mod.__name__) for mod in self._modifiers]
        if mod_str_list:
            mod_str = ", ".join(mod_str_list)
        else:
            mod_str = "none"

        return "\n".join(
            [
                f"{self.__name__}",
                f"  signature: {', '.join(sig_list)}",
                f"  returns: {', '.join(self.returns)}",
                f"  handler: {self._handler_info}",
                f"  modifiers: {mod_str}",
                f"{self._graph.graph.get('doc', '')}",
            ]
        )

    @staticmethod
    def is_graph_valid(G):
        """Check if model_graph is valid to build a executable

        ``mmodel`` does not allow cycle graph, graph with isolated nodes,
        and all nodes have callable attributes defined.
        The method is bind to Model class because the following features
        are specific for ``Model`` class
        """

        assert nx.is_directed(G), "invalid graph: undirected graph"
        assert not nx.recursive_simple_cycles(G), "invalid graph: graph contains cycles"
        assert not list(nx.isolates(G)), "invalid graph: graph contains isolated nodes"

        assert is_node_attr_defined(
            G, "obj"
        ), "invalid graph: graph contains nodes with undefined callables"

        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "returns"), (
            "invalid graph: graph contains nodes with undefined callables returns, "
            "recommend using ModelGraph add_node_object method to add node object"
        )
        assert is_node_attr_defined(G, "sig"), (
            "invalid graph: graph contains nodes with undefined callables signatures, "
            "recommend using ModelGraph add_node_object method to add node object"
        )
        assert is_edge_attr_defined(G, "val"), (
            "invalid graph: graph contains edges with undefined variable attributes, "
            "recommend using ModelGraph add_node_object method to add node object"
        )

        return True
