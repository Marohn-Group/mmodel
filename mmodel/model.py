from mmodel.utility import (
    modify_func,
    is_node_attr_defined,
    is_edge_attr_defined,
    modelgraph_returns,
    EditMixin,
    ReprMixin,
)

import networkx as nx
from mmodel.metadata import modelformatter
from mmodel.signature import restructure_signature
from inspect import signature
from mmodel.visualizer import visualizer


class Model(EditMixin, ReprMixin):
    """Create the model callable.

    :param str name: Model name
    :param object graph: Graph instance (digraph)
    :param class handler: Handler class that handles model execution and
        the keyword arguments.
    :param dict handler_kwargs: keyword arguments for the handler class.
    :param list modifiers: modifiers used for the whole graph model executable.
    :param list returns: If not provided, the returns are the returns of the terminal
        roots. The order of model returns defaults to the topological order.
    :param str doc: model docstring
    :param dict param_defaults: default values for the model signature.
    :param bool kw_only: whether to convert signature to keyword-only signature
    """

    def __init__(
        self,
        name,
        graph,
        handler,
        handler_kwargs: dict = None,
        modifiers: list = None,
        returns: list = None,
        param_defaults: dict = None,
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
        self._param_defaults = param_defaults or {}
        self.doc = self.__doc__ = doc

        # update the kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        # create the runner using handler
        self._runner = handler(self._graph, self._returns, **self._handler_kwargs)
        self._runner.__name__ = self.name
        # final callable
        # model_func can be modified externally
        self.model_func = modify_func(self._runner, self._modifiers)
        # apply defaults to model_func
        self.model_func.__signature__ = restructure_signature(
            signature(self.model_func), self._param_defaults
        )

    @property
    def order(self):
        """The order of the node execution."""
        return list(zip(*self._runner.order))[0]

    @property
    def signature(self):
        """Model signature for inspection."""
        return self.__signature__

    @property
    def __signature__(self):
        """Model signature for inspection."""

        return self.model_func.__signature__

    @property
    def graph(self):
        """The graph attribute outputs a copy of the graph."""
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
    def param_defaults(self):
        """Shallow copy of the defaults."""
        return self._param_defaults.copy()

    @property
    def handler_kwargs(self):
        """Shallow copy of the handler arguments."""
        return self._handler_kwargs.copy()

    def __call__(self, *args, **kwargs):
        """Execute the model.

        The inputs from the keyword arguments are parsed and passed to the
        the handler class.
        """
        bound = self.signature.bind(*args, **kwargs)
        # defaults are added in the signature property
        bound.apply_defaults()
        return self.model_func(**bound.arguments)

    def __str__(self):
        return modelformatter(self)

    @staticmethod
    def _is_valid_graph(G):
        """Check if the model graph is valid to build an executable.

        The ``Model`` class does not allow cycle graphs.
        The method is bound to the Model class because the features
        are specific to ``Model`` class.
        """

        assert nx.is_directed(G), f"invalid graph ({G.name}): undirected graph."
        assert not nx.recursive_simple_cycles(
            G
        ), f"invalid graph ({G.name}): graph contains cycles."

        assert is_node_attr_defined(G, "node_object")
        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "output")
        assert is_node_attr_defined(G, "signature")
        assert is_edge_attr_defined(G, "output")
        return True

    def get_node(self, node):
        """Quick access to node within the model."""

        return self._graph.nodes[node]

    def get_node_object(self, node):
        """Quick access to node object within the model."""

        return self._graph.nodes[node]["node_object"]

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

    def edit_node(self, node, **kwargs):
        """Edit node object.

        A new model is created in the process.
        """

        graph = self._graph.edit_node(node, **kwargs)

        return self.edit(graph=graph)

    def edit(self, **kwargs):
        """Edit components of the model to create a new model.

        Editing the graph component of the model is not recommended.
        Although it does create a new model, "edit" is for building
        a new model with the same graph.
        """

        # reset returns when the graph is changed
        if "graph" in kwargs and "returns" not in kwargs:
            kwargs["returns"] = None

        edit_dict = self.edit_dict
        edit_dict.update(kwargs)

        return self.__class__(**edit_dict)
