from mmodel.utility import (
    parse_input,
    parse_modifiers,
    content_wrap,
    is_node_attr_defined,
    is_edge_attr_defined,
)
from mmodel.draw import draw_graph
import networkx as nx


class Model:
    """Create model executable.

    :param str name: Model name
    :param object graph: ModelGraph instance (digraph)
    :param class handler: Handler class that handles model execution and
        the keyword arguments. The parameter format is (HandlerClass, {})
        By default, the handler takes the graph as the first parameter.
        For additional arguments, add an argument to the dictionary afterward.
    :param list modifiers: modifiers used for the whole graph model executable.
        The parameter is Optional and defaults to an empty list. For each modifier,
        the format is (modifier, {}). All modifiers should have the function as
        the first argument.
    :param str description: model description
    :param list returns: The order of returns of the model; defaults to the
        topological search.
    """

    def __init__(
        self,
        name,
        graph,
        handler,
        modifiers: list = None,
        description: str = "",
        returns: list = None,
    ):

        assert self._is_valid_graph(graph)
        self.name = self.__name__ = name

        # create a copy of the graph
        self._graph = nx.freeze(graph.deepcopy())
        self.returns = returns or self._graph.returns  # tuples
        self.modifiers = modifiers or list()
        self.handler = handler
        self.description = description

        handler_class, handler_kwargs = handler

        executor = handler_class(name, self._graph, self.returns, **handler_kwargs)

        for mdf, kwargs in self.modifiers:
            executor = mdf(executor, **kwargs)

        self.__signature__ = executor.__signature__

        # final callable
        self.executor = executor

    def __call__(self, *args, **kwargs):

        # process inputs
        inputs = parse_input(self.__signature__, *args, **kwargs)

        return self.executor(**inputs)

    def __str__(self):
        """Output callable information."""

        return self.metadata()

    def metadata(self, full=True, wrap_width=80):
        """Parse metadata string of the Model instance."""

        # use tuple if there are multiple returns
        # else use returns directly.
        return_len = len(self.returns)
        if return_len == 0:
            returns_str = "None"
        elif return_len == 1:
            returns_str = self.returns[0]
        else:
            returns_str = f"({', '.join(self.returns)})"

        metadata_list = [
            f"{self.__name__}{self.__signature__}",
            f"returns: {returns_str}",
            f"handler: {self.handler[0].__name__}"
            f"({', '.join(repr(v) for v in self.handler[1].values())})",
        ]

        metadata_list.extend(parse_modifiers(self.modifiers))

        if full:
            metadata_list.extend(["", self.description])

        wrapped_list = content_wrap(metadata_list, width=wrap_width)

        return "\n".join(wrapped_list).rstrip()

    @staticmethod
    def _is_valid_graph(G):
        """Check if the model graph is valid to build an executable.

        ``mmodel`` does not allow cycle graphs, graphs with isolated nodes,
        and all nodes have callable attributes defined.
        The method is bound to the Model class because the features
        are specific to ``Model`` class.
        """

        assert nx.is_directed(G), f"invalid graph ({G.name}): undirected graph."
        assert not nx.recursive_simple_cycles(
            G
        ), f"invalid graph ({G.name}): graph contains cycles."

        assert is_node_attr_defined(G, "func", "callable")
        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "output")
        assert is_node_attr_defined(G, "sig", "signature")
        assert is_edge_attr_defined(G, "var", "variable")

        return True

    @property
    def graph(self):
        """The graph attribute output a copy of the graph."""
        return self._graph.deepcopy()

    def get_node(self, node):
        """Quick access to node within the model."""

        return self._graph.nodes[node]

    def get_node_func(self, node):
        """Quick access to node base callable within the model.
        
        The function helps extract the original function within
        the node.
        """

        return self._graph.nodes[node]["_func"]

    def node_metadata(self, node, full=True, wrap_width=80):
        """View a specific node."""

        return self._graph.node_metadata(node, full=True, wrap_width=80)

    def draw(self, style="full", export=None, wrap_width=30):
        """Draw the graph of the model.

        Draws the default styled graph.

        :param str style: there are three styles, plain, short, and full.
            Plain shows nodes only, short shows part of the metadata, and
            long shows all the metadata.
        :param str export: filename to save the graph as. The file extension
            is needed.

        """

        return draw_graph(self._graph, self.metadata(), style, export, wrap_width)
