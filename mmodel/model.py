from mmodel.utility import (
    modify_func,
    construction_dict,
    is_node_attr_defined,
    is_edge_attr_defined,
    modelgraph_returns,
)

import networkx as nx
from mmodel.metadata import modelformatter
from mmodel.signature import add_defaults
from inspect import signature
from mmodel.visualizer import visualizer


class Model:
    """Create model callable.

    :param str name: Model name
    :param object graph: Graph instance (digraph)
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
        handler_kwargs: dict = None,
        modifiers: list = None,
        returns: list = None,
        defaults: dict = None,
        doc: str = "",
        **kwargs,
    ):
        assert self._is_valid_graph(graph)
        self.name = self.__name__ = name
        # create a copy of the graph
        self._graph = nx.freeze(graph.deepcopy())
        self._returns = returns or modelgraph_returns(graph)  # tuples
        self._modifiers = modifiers or list()
        self.handler = handler
        self._handler_kwargs = handler_kwargs or {}
        self._defaults = defaults or {}
        self.doc = doc
        self.__dict__.update(kwargs)

        # create the runner using handler
        self._runner = handler(self._graph, self._returns, **self._handler_kwargs)
        self._runner.__name__ = self.name
        # final callable
        self._model_func = modify_func(self._runner, self._modifiers)
        self.__signature__ = add_defaults(signature(self._model_func), self._defaults)

    @property
    def signature(self):
        """Model signature for inspection."""
        return self.__signature__

    @property
    def graph(self):
        """The graph attribute output a copy of the graph."""
        return self._graph.deepcopy()

    @property
    def returns(self):
        """Shallow copy of the returns."""
        return self._returns.copy()

    @property
    def modifiers(self):
        """Shallow copy of the modifiers."""
        return self._modifiers.copy()

    @property
    def defaults(self):
        """Shallow copy of the defaults."""
        return self._defaults.copy()

    @property
    def handler_kwargs(self):
        """Shallow copy of the handler arguments."""
        return self._handler_kwargs.copy()

    @property
    def model_func(self):
        """The model function."""
        return self._model_func

    def __call__(self, *args, **kwargs):
        """Execute the model.

        The inputs from the keyword arguments are parsed and passed to the
        the handler class.
        """

        bound = self.signature.bind(*args, **kwargs)
        # defaults are added in the signature property
        bound.apply_defaults()
        return self._model_func(**bound.arguments)

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

        assert is_node_attr_defined(G, "node_obj")
        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "output")
        assert is_node_attr_defined(G, "signature")
        assert is_edge_attr_defined(G, "var", "variable")
        return True

    def get_node(self, node):
        """Quick access to node within the model."""

        return self._graph.nodes[node]

    def get_node_obj(self, node):
        """Quick access to node object within the model."""

        return self._graph.nodes[node]["node_obj"]

    def visualize(self, outfile=None):
        """Draw the graph of the model.

        Draws the default styled graph.

        :param str style: there are three styles, plain, short, and verbose.
            Plain shows nodes only, short shows part of the metadata, and
            long shows all the metadata.
        :param str export: filename to save the graph as. The file extension
            is needed.
        """

        return visualizer(self._graph, str(self), outfile)

    def __str__(self):
        return modelformatter(self)

    def edit_node(self, node, **kwargs):
        """Edit node object.

        A new model is created in the process.
        """

        graph = self._graph.edit_node(node, **kwargs)

        return self.edit(graph=graph)

    def edit(self, **kwargs):
        """Edit components of the model to create a new model.

        It is not recommended to edit the graph component of the model.
        Although it does create a new model, "edit" is for creating
        a new model with the same graph.
        """

        constructor_dict = construction_dict(
            self, ["graph", "returns", "modifiers", "handler_kwargs", "defaults"]
        )
        constructor_dict.update(kwargs)

        return self.__class__(**constructor_dict)
