import inspect
from mmodel.utility import parse_input, is_node_attr_defined, is_edge_attr_defined
import networkx as nx


class Model:
    """Create model executable

    :param object model_graph: ModelGraph instance
    :param class handler: Handler class that handles model execution
    :param dict handler_args: additional handler argument that is not model_graph
        and add_returns. Optional, default to a empty dict.
    :param list modifiers: modifiers used for the whole graph model executable.
        Optional, defaults to a empty list.
    :param list add_returns: additional parameters to return. The parameter is
        used for retriving intermediate values of the graph model.
        Optional, defaults to a empty list.
    """

    def __init__(
        self, model_graph, handler, handler_args={}, modifiers=[], add_returns=[]
    ):

        assert self.is_graph_valid(model_graph)

        self.__name__ = f"{model_graph.name} model"
        self.model_graph = model_graph.copy()

        executor = handler(model_graph, add_returns, **handler_args)

        for mdf in modifiers:
            executor = mdf(executor)

        self.__signature__ = executor.__signature__
        self.returns = executor.returns
        self.executor = executor

        self.handler_name = handler.__name__

    def __call__(self, *args, **kwargs):

        # process input
        data_input = parse_input(self.__signature__, *args, **kwargs)

        return self.executor(**data_input)

    def __str__(self):
        """Output callable information"""

        sig_list = [str(param) for param in self.__signature__.parameters.values()]

        return "\n".join(
            [
                f"{self.__name__}",
                f"signature - {', '.join(sig_list)}",
                f"returns - {', '.join(self.returns)}",
                f"handler - {self.handler_name}",
                f"{self.model_graph.graph.get('doc', '')}",
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
        assert is_edge_attr_defined(G, 'val'), (
            "invalid graph: graph contains edges with undefined variable attributes, "
            "recommend using ModelGraph add_node_object method to add node object"
        )

        return True
