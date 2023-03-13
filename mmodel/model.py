import inspect
from mmodel.utility import (
    parse_input,
    is_node_attr_defined,
    is_edge_attr_defined,
    model_returns,
)
from mmodel.filter import subnodes_by_outputs
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
        modifiers: list = None,
        description: str = ""
        # returns: list = None,
    ):

        assert self._is_valid_graph(graph)
        self.name = self.__name__ = name

        # create a copy of the graph
        self._graph = nx.freeze(graph.deepcopy())
        self.returns = model_returns(self._graph) # tuples
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

        assert nx.is_directed(G), f"invalid graph ({G.name}): undirected graph"
        assert not nx.recursive_simple_cycles(
            G
        ), f"invalid graph ({G.name}): graph contains cycles"

        assert is_node_attr_defined(G, "func", "callable")
        # the following might occur when the node object is incorrectly constructed
        assert is_node_attr_defined(G, "output")
        assert is_node_attr_defined(G, "sig", "signature")
        assert is_edge_attr_defined(G, "var", "variable")

        return True

    @property
    def graph(self):
        """The graph attribute output a copy of the graph"""
        return self._graph.deepcopy()


    def get_node(self, node):
        """Quick access to node within the model"""

        return self._graph.nodes[node]

    def get_node_object(self, node):
        """Quick access to node callable within the model"""

        return self._graph.nodes[node]["func"]

    def view_node(self, node):
        """View a specific node"""

        return self._graph.view_node(node)

    def draw(self, method: callable = draw_graph, export=None):
        """Draw the graph of the model

        :param str export: filename to export to, extension name required.

        A drawing is provided. Defaults to ``draw_graph``.
        '\l' forces the label to align left when it is defined after the line.
        Returns the dot_graph (can be rendered in Jupyter notebook).
        If the export parameter is specified, the dot file is saved to file.
        See graphviz.render() for more rendering options.
        """

        dot_graph = method(self._graph, label=str(self).replace("\n", "\l") + "\l")
        if export:
            dot_graph.render(outfile=export)

        return dot_graph
