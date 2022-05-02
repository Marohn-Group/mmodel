import inspect
import networkx as nx


class ModelGraph(nx.DiGraph):

    """Base class for mmodel Graph

    ModelGraph inherits from `networkx.DiGraph()`, which has all `DiGraph`
    methods.

    The graph adds "type" attribute to the graph attribute. The additional
    graph operations are added: add grouped edges and add node objects.
    Method add grouped edges one of the node to be a list.
    Method add node object update nodes with the node callable 'obj' and returns.
    The method adds callable signature 'sig' to the node attribute
    """

    # add the graph attribute
    # this is used for checking
    graph_attr_dict = {"type": "ModelGraph"}

    def single_graph_attr_dict(self):
        """Add type to graph"""
        return self.graph_attr_dict

    graph_attr_dict_factory = single_graph_attr_dict

    def add_node_object(self, node, obj, returns):
        """Add or update the functions of existing node

        If the node does not exist, create the node.
        In the end, the edge attributes are re-determined
        """

        if node not in self.nodes:
            self.add_node(node)

        sig = inspect.signature(obj)
        self.nodes[node]["obj"] = obj
        self.nodes[node]["sig"] = sig
        self.nodes[node]["returns"] = returns
        self.update_graph()

    def add_node_objects_from(self, node_objects):
        """Update the functions of existing nodes
        
        The method is the same as add node object
        """

        for node, obj, returns in node_objects:
            self.add_node_object(node, obj, returns)

    def add_grouped_edge(self, u, v):
        """Add linked edge

        For mmodel, a group edge (u, v) allows u or v
        to be a list of nodes. Represents several nodes
        flow into one node or the other way around.
        """

        if isinstance(u, list) and isinstance(v, list):
            raise Exception(f"only one edge node can be a list")
        
        # use add edges from to run less update graph
        # currently a compromise 
        if isinstance(u, list):
            self.add_edges_from([(_u, v) for _u in u])
        elif isinstance(v, list):
            self.add_edges_from([(u, _v) for _v in v])
        else:  # neither is a list
            self.add_edge(u, v)

    def add_grouped_edges_from(self, group_edges):
        """Add edges from grouped values"""

        for u, v in group_edges:
            self.add_grouped_edge(u, v)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """Modify add_edge to update the edge attribute in the end"""
        
        super().add_edge(u_of_edge, v_of_edge, **attr)
        self.update_graph()

    def add_edges_from(self, ebunch_to_add, **attr):
        """Modify add_edges_from to update the edge attributes"""

        super().add_edges_from(ebunch_to_add, **attr)
        self.update_graph()

    def update_graph(self):
        """Update edge attributes based on node objects and edges"""

        for u, v in self.edges:
            u_rts = set(self.nodes[u].get("returns", ()))
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
