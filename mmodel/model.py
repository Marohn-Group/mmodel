import inspect
from mmodel.utility import parse_input, is_node_attr_defined, is_edge_attr_defined
from mmodel.draw import draw_graph
import networkx as nx


class Model:
    """Create model executable

    :param object graph: ModelGraph instance (digraph)
    :param class handler: Handler class that handles model execution and the keyword
        arguments. The parameter format is (HandlerClass, {})
        By default, the handler takes the graph as the first parameter.
        For additional arguments, add argument to dictionary afterwards.
    :param list modifiers: modifiers used for the whole graph model executable.
        Optional, defaults to an empty list. For each modifier, the format is
        (modifier, {}). All modifiers should have function as the first argument
    """

    def __init__(self, graph, handler, description: str = "", modifiers: list = []):

        assert self._is_valid_graph(graph)

        self.__name__ = f"{graph.name} model"

        # store only the copy of the graph, note this is not the same copy
        # used by the handler
        # modify self._graph does not change the model itself
        self._graph = nx.freeze(graph.deepcopy())
        self._modifiers = modifiers
        self._handler = handler
        self.description = description

        handler_class, handler_kwargs = handler
        executor = handler_class(self._graph, **handler_kwargs)

        for mdf, kwargs in modifiers:
            executor = mdf(executor, **kwargs)

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
        handler_str = f"{self._handler[0].__name__}, {self._handler[1]}"

        modifier_str_list = [
            f"{func.__name__}, {kwargs}" for func, kwargs in self._modifiers
        ]
        modifier_str = f"[{', '.join(modifier_str_list)}]"

        return "\n".join(
            [
                f"{self.__name__}",
                f"  signature: {', '.join(sig_list)}",
                f"  returns: {', '.join(self.returns)}",
                f"  handler: {handler_str}",
                f"  modifiers: {modifier_str}",
                f"{self.description}",
            ]
        ).rstrip()

    @staticmethod
    def _is_valid_graph(G):
        """Check if model graph is valid to build an executable

        ``mmodel`` does not allow cycle graphs, graphs with isolated nodes,
        and all nodes have callable attributes defined.
        The method is bound to Model class because the features
        are specific to ``Model`` class.
        """

        assert nx.is_directed(G), "invalid graph: undirected graph"
        assert not nx.recursive_simple_cycles(G), "invalid graph: graph contains cycles"
        assert not list(nx.isolates(G)), "invalid graph: graph contains isolated nodes"

        assert is_node_attr_defined(
            G, "func"
        ), "invalid graph: graph contains nodes with undefined callables"

        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "returns"), (
            "invalid graph: graph contains nodes with undefined callables returns, "
            "recommend using ModelGraph set_node_object method to add node object"
        )
        assert is_node_attr_defined(G, "sig"), (
            "invalid graph: graph contains nodes with undefined callables signatures, "
            "recommend using ModelGraph set_node_object method to add node object"
        )
        assert is_edge_attr_defined(G, "val"), (
            "invalid graph: graph contains edges with undefined variable attributes, "
            "recommend using ModelGraph set_node_object method to add node object"
        )

        return True

    def get_node(self, node):
        """Quick access to node within the model"""

        return self._graph.nodes[node]

    def get_node_object(self, node):
        """Quick access to node callable within the model"""

        return self._graph.nodes[node]["func"]

    def view_node(self, node):
        """View a specific node"""

        return self._graph.view_node(node)

    def draw(self, method: callable = draw_graph):
        """Draw the graph of the model

        A drawing is provided. Defaults to ``draw_graph``.
        '\l' forces the label to align left when it is defined after the line.
        """

        return method(self._graph, str(self).replace("\n", "\l") + "\l")
