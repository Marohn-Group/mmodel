import inspect
import networkx as nx
from mmodel.utility import graph_returns, graph_signature
from mmodel.draw import draw_graph, draw_plain_graph
from mmodel.doc import parse_description_graph, parse_description_doc


class MGraph(nx.DiGraph):

    """Base class for mmodel Graph

    ModelGraph inherits from `networkx.DiGraph()`, which has all `DiGraph` methods.
    Graphs inherits ModelGraph needs to define the nodes first, with the required
    attributes "func" and "returns". The func is the default function and returns is list of
    return parameters for the graph. The two names are used to avoid collision with python
    default variable "return" and "callable"
    The edges requires the attribute "parameters", which is the intermediate parameters passed down
    from one node to another.

    :param str name: Model name, defaults to class name. The name is attached to
        the graph.
    """

    def __init__(self, name="", doc="", **attr):

        super().__init__(name=name, doc=doc, **attr)

    def add_node(self, node_for_adding, node_obj, returns, **attr):
        """re-define the add_node method

        Require arguments func and returns"""

        if callable(node_obj):
            sig = inspect.signature(node_obj)
        else:
            raise Exception(f"Node object type {type(node_obj)} not supported")

        super().add_node(
            node_for_adding,
            node_obj=node_obj,
            returns=returns,
            signature=sig,
            **attr,
        )

    def add_nodes_from(self, nodes_for_adding, **attr):
        """re-define the add_nodes_from method

        TODO
            check node name duplications
        """

        try:
            nodes = []
            for n, ndict in nodes_for_adding:

                if ("node_obj" not in ndict) or ("returns" not in ndict):

                    raise Exception(
                        "Node list missing attribute node_obj or returns"
                    )
                node_obj = ndict["node_obj"]
                if callable(node_obj):
                    ndict["signature"] = inspect.signature(node_obj)
                else:
                    raise Exception(f"Node object type {type(node_obj)} not supported")

                nodes.append([n, ndict])
        except ValueError:
            raise Exception("Node list missing node attributes")

        super().add_nodes_from(nodes, **attr)

    def add_edge(self, u_of_edge, v_of_edge, parameters, **attr):
        """re-define the add_edge method"""

        if u_of_edge not in self._succ:
            raise Exception(f"Node {u_of_edge} is not defined")
        if v_of_edge not in self._succ:
            raise Exception(f"Node {v_of_edge} is not defined")

        super().add_edge(u_of_edge, v_of_edge, parameters=parameters, **attr)

    def add_edges_from(self, ebunch_to_add, **attr):
        """re-define the add_edges_from method"""

        edges = []
        try:
            for u_of_edge, v_of_edge, edict in ebunch_to_add:
                if u_of_edge not in self._succ:
                    raise Exception(f"Node {u_of_edge} is not defined")
                if v_of_edge not in self._succ:
                    raise Exception(f"Node {v_of_edge} is not defined")
                if "parameters" not in edict:
                    raise Exception("Edge attribute parameters not defined")

                edges.append([u_of_edge, v_of_edge, edict])
        except ValueError:
            raise Exception("Edge attribute parameters not defined")

        super().add_edges_from(edges, **attr)

    @property
    def doc(self):
        """doc property (for easier access)"""
        return self.graph["doc"]

    def draw_graph(self, show_detail=False):
        """Draw graph"""
        if show_detail:
            label = parse_description_graph(self._long_description(False))
            return draw_graph(self, self.name, label)
        else:
            label = parse_description_graph(self._short_description())
            return draw_plain_graph(self, self.name, label)

    def _short_description(self):
        """graph short documentation"""

        short_docstring = self.doc.partition("\n")[0]

        des_list = [("name", self.name), ("doc", short_docstring)]

        return des_list

    def _long_description(self, long_docstring=True):
        """graph long documentation"""
        if long_docstring:
            doc = self.doc
        else:
            doc = self.doc.partition("\n")[0]

        des_list = [
            ("name", self.name),
            ("doc", doc),
            ("graph type", str(self.__class__)),
            ("parameters", str(graph_signature(self))),
            ("returns", ", ".join(graph_returns(self))),
        ]

        return des_list

    def __repr__(self):
        """Show instance description"""
        title = f"{self.__class__.__name__} instance\n\n"
        return title + parse_description_doc(self._long_description()).expandtabs(4)
