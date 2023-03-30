from mmodel.utility import parse_input, is_node_attr_defined, is_edge_attr_defined
from mmodel.metadata import modelformatter, textwrap80, format_metadata
from mmodel.draw import draw_graph
import networkx as nx


class Model:
    """Create model callable.

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

    _model_keys = ["name", "graph", "handler", "modifiers", "description", "returns"]

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
        self.execution_order = [node for node, _ in executor.order]

        for mdf, kwargs in self.modifiers:
            executor = mdf(executor, **kwargs)

        self.__signature__ = executor.__signature__

        # final callable
        self._executor = executor

    def __call__(self, *args, **kwargs):
        """Execute the model.

        The inputs from the keyword arguments are parsed and passed to the
        the handler class.
        """

        # process inputs
        inputs = parse_input(self.__signature__, *args, **kwargs)

        return self._executor(**inputs)

    def _metadata_dict(self, verbose):
        """Return a dictionary with metadata keys."""

        short_dict = {"model": self, "returns": self.returns}

        additonal_dict = {
            "graph": self._graph,
            "handler": self.handler,
            "modifiers": self.modifiers,
            "description": self.description,
        }

        if verbose:
            return {**short_dict, **additonal_dict}
        else:
            return short_dict

    def metadata_str(
        self, verbose=True, formatter=modelformatter, textwrapper=textwrap80
    ):
        """Parse metadata string of the Model instance."""
        return format_metadata(self._metadata_dict(verbose), formatter, textwrapper)

    def __str__(self):
        """Output callable information."""

        str_list = self.metadata_str()
        return "\n".join(str_list).rstrip()

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

    def node_metadata(self, *args, **kwargs):
        """View a specific node."""

        return self._graph.node_metadata(*args, **kwargs)

    def draw(self, style="verbose", export=None):
        """Draw the graph of the model.

        Draws the default styled graph.

        :param str style: there are three styles, plain, short, and verbose.
            Plain shows nodes only, short shows part of the metadata, and
            long shows all the metadata.
        :param str export: filename to save the graph as. The file extension
            is needed.
        """

        return draw_graph(self._graph, str(self), style, export)

    def edit(self, **kwargs):
        """Edit components of the model to create a new model.

        It is not recommended to edit the graph component of the model.
        Although it does create a new model, but "edit" is for creating
        a new model with the same graph.
        """

        model_dict = {key: getattr(self, key) for key in self._model_keys}
        return self.__class__(**{**model_dict, **kwargs})
