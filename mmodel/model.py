import inspect
from mmodel.utility import (
    parse_input,
    is_node_attr_defined,
    is_edge_attr_defined,
    model_returns,
)
from mmodel.filter import subgraph_by_returns
from mmodel.draw import draw_graph
import networkx as nx
from textwrap import wrap as txtwrap


class Model:
    """Create model executable

    :param str name: Model name
    :param str description: Model description
    :param object graph: ModelGraph instance (digraph)
    :param class handler: Handler class that handles model execution and the keyword
        arguments. The parameter format is (HandlerClass, {})
        By default, the handler takes the graph as the first parameter.
        For additional arguments, add argument to dictionary afterwards.
    :param list modifiers: modifiers used for the whole graph model executable.
        Optional, defaults to an empty list. For each modifier, the format is
        (modifier, {}). All modifiers should have function as the first argument
    :param str description: model description
    :param list returns: the order of returns of the model defaults to the topological search
    :param str output: output name of the model, defaults to terminal node name
        if there are multiple terminal name, defaults to "combined_output"
    """

    def __init__(
        self,
        name,
        graph,
        handler,
        modifiers=None,
        description: str = "",
        returns: list = None,
    ):

        assert self._is_valid_graph(graph)
        self.__name__ = name

        # store only the copy of the graph, note this is not the same copy
        # used by the handler
        # modify self.graph does not change the model itself
        # self.graph = nx.freeze(graph.deepcopy())

        graph_returns = model_returns(graph)
        self.base_graph = nx.freeze(graph)
        self.returns = returns or graph_returns
        # if there are nodes in graph_returns that is not in returns
        # this means that some nodes are not needed for the calculation
        if set(graph_returns) - set(self.returns):
            # returns subgraph view of the original graph, is also freezed
            self.graph = subgraph_by_returns(self.base_graph, returns)
        else:
            self.graph = self.base_graph

        self.modifiers = modifiers or list()
        self.handler = handler
        self.description = description

        handler_class, handler_kwargs = handler

        executor = handler_class(name, self.graph, self.returns, **handler_kwargs)

        for mdf, kwargs in self.modifiers:
            executor = mdf(executor, **kwargs)

        self.__signature__ = executor.__signature__
        # self.output = executor.output
        # final callable
        self.executor = executor

    def __call__(self, *args, **kwargs):

        # process inputs
        inputs = parse_input(self.__signature__, *args, **kwargs)

        return self.executor(**inputs)

    def __str__(self):
        """Output callable information"""

        handler_str = f"{self.handler[0].__name__}, {self.handler[1]}"

        modifier_str_list = [
            f"{func.__name__}, {kwargs}" for func, kwargs in self.modifiers
        ]
        modifier_str = f"[{', '.join(modifier_str_list)}]"

        model_str = [
            f"{self.__name__}{self.__signature__}",
            f"  returns: {', '.join(self.returns)}",
            f"  handler: {handler_str}",
            f"  modifiers: {modifier_str}",
            f"{self.description}",
        ]

        # wrap string
        model_str_wrapped = []
        for s in model_str:
            model_str_wrapped.extend(txtwrap(s, 80))

        return "\n".join(model_str_wrapped).rstrip()

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
        assert is_node_attr_defined(G, "output"), (
            "invalid graph: graph contains nodes with undefined callables output, "
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

        return self.graph.nodes[node]

    def get_node_object(self, node):
        """Quick access to node callable within the model"""

        return self.graph.nodes[node]["func"]

    def view_node(self, node):
        """View a specific node"""

        return self.graph.view_node(node)

    def draw(self, method: callable = draw_graph):
        """Draw the graph of the model

        A drawing is provided. Defaults to ``draw_graph``.
        '\l' forces the label to align left when it is defined after the line.
        """

        return method(self.graph, label=str(self).replace("\n", "\l") + "\l")
