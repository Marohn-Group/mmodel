import inspect
import networkx as nx


class ModelGraph(nx.DiGraph):

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

    # add the graph attribute
    # this is used for checking
    graph_attr_dict = {"type": "ModelGraph"}

    def single_graph_attr_dict(self):
        """Add type to graph"""
        return self.graph_attr_dict

    graph_attr_dict_factory = single_graph_attr_dict

    def update_node_object(self, node, obj, rts, **kwargs):
        """Update the functions of existing node"""

        sig = inspect.signature(obj)
        self.nodes[node]["obj"] = obj
        self.nodes[node]["sig"] = sig
        self.nodes[node]["rts"] = rts
        self.nodes[node].update(kwargs)

        self._update_edge_attrs()

    def update_node_objects_from(self, node_objects):
        """Update the functions of exisiting nodes"""

        for node, obj, rts in node_objects:
            sig = inspect.signature(obj)
            self.nodes[node]["obj"] = obj
            self.nodes[node]["sig"] = sig
            self.nodes[node]["rts"] = rts

        self._update_edge_attrs()

    def add_linked_edges_from(self, linked_edges):
        """Add edges from linked value"""

        for u, v in linked_edges:
            if isinstance(u, list):
                for _u in u:
                    self.add_edge(_u, v)
            elif isinstance(v, list):
                for _v in v:
                    self.add_edge(u, _v)

    def _update_edge_attrs(self):
        """Update edge attributes"""

        for u, v in self.edges:
            u_rts = set(self.nodes[u].get("rts", ()))
            v_sig = self.nodes[v].get("sig", None)

            if v_sig is not None:
                v_params = set(v_sig.parameters.keys())
                self.edges[u, v]["val"] = list(u_rts.intersection(v_params))

    def __str__(self):
        """Output graph information"""
        # default string is the string output of networkx.Graph
        default_str = "".join(
            [
                type(self).__name__,
                f" named {self.name!r}" if self.name else "",
                f" with {self.number_of_nodes()} nodes and {self.number_of_edges()} edges",
            ]
        )
        docstring = self.graph.get("doc", "")

        return f"{default_str}\n\n{docstring}"
