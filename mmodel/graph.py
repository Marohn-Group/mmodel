import inspect
from subprocess import call
import networkx as nx
from mmodel.utility import graph_signature


class MGraph(nx.DiGraph):

    """Base class for mmodel Graph

    ModelGraph inherits from `networkx.DiGraph()`, which has all `DiGraph` methods.
    Graphs inherits ModelGraph needs to define the nodes first, with the required
    attributes "func" and "return_params". The func is the default function and return_params is list of
    return parameters for the graph. The two names are used to avoid collision with python
    default variable "return" and "callable"
    The edges requires the attribute "interm_params", which is the intermediate parameters passed down
    from one node to another.

    :param str name: Model name, defaults to class name. The name is attached to
        the graph.
    """

    def __init__(self, name=None):

        name = name or self.__class__.__name__

        super().__init__(name=name)

    def add_node(self, node_for_adding, node_obj, return_params, **attr):
        """re-define the add_node method

        Require arguments func and return_params"""

        if callable(node_obj):
            sig = inspect.signature(node_obj)
        else:
            raise Exception(f"Node object type {type(node_obj)} not supported")

        super().add_node(
            node_for_adding,
            node_obj=node_obj,
            return_params=return_params,
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
                
                if ("node_obj" not in ndict) or ("return_params" not in ndict):

                    raise Exception(
                        "Node list missing attribute node_obj or return_params"
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

    def add_edge(self, u_of_edge, v_of_edge, interm_params, **attr):
        """re-define the add_edge method"""

        if u_of_edge not in self._succ:
            raise Exception(f"Node {u_of_edge} is not defined")
        if v_of_edge not in self._succ:
            raise Exception(f"Node {v_of_edge} is not defined")

        super().add_edge(u_of_edge, v_of_edge, interm_params=interm_params, **attr)

    def add_edges_from(self, ebunch_to_add, **attr):
        """re-define the add_edges_from method"""

        edges = []
        try:
            for u_of_edge, v_of_edge, edict in ebunch_to_add:
                if u_of_edge not in self._succ:
                    raise Exception(f"Node {u_of_edge} is not defined")
                if v_of_edge not in self._succ:
                    raise Exception(f"Node {v_of_edge} is not defined")
                if "interm_params" not in edict:
                    raise Exception("Edge attribute interm_params not defined")

                edges.append([u_of_edge, v_of_edge, edict])
        except ValueError:
            raise Exception("Edge attribute interm_params not defined")

        super().add_edges_from(edges, **attr)
