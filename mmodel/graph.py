import networkx as nx
from mmodel.visualizer import plain_visualizer
from copy import deepcopy
from mmodel.filter import subnodes_by_inputs, subnodes_by_outputs
from mmodel.utility import replace_subgraph
from itertools import product
from collections import defaultdict


class Graph(nx.DiGraph):
    """Create model graphs.

    mmodel.Graph inherits from `networkx.DiGraph()`.

    The class adds the "type" attribute to the graph attribute. The factory method
    returns a copy of the dictionary. It is equivalent to
    ``{"type": "mmodel_graph"}.copy()`` when called.

    The additional graph operations are added:
    - add_grouped_edges and set_node_objects.
    - Method ``add_grouped_edges``, cannot have both edges list.
    - Method ``set_node_object`` updates nodes with the node callable "func" and output.
    - The method adds 'signature' to the node attribute.
    """

    graph_attr_dict_factory = {"type": "mmodel_graph"}.copy

    def set_node_object(self, node_object):
        """Add or update the functions of an existing node."""
        self.nodes[node_object.name]["node_object"] = node_object
        self.nodes[node_object.name]["signature"] = node_object.signature
        self.nodes[node_object.name]["output"] = node_object.output
        self.update_graph()

    def set_node_objects_from(self, node_objects: list):
        """Update the functions of existing nodes.

        The method is the same as adding a node object.
        """

        for node_object in node_objects:
            # unzipping works for input with or without modifiers
            self.set_node_object(node_object)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """Modify add_edge to update the edge attribute in the end."""

        super().add_edge(u_of_edge, v_of_edge, **attr)
        self.update_graph()

    def add_edges_from(self, ebunch_to_add, **attr):
        """Modify add_edges_from to update the edge attributes."""

        super().add_edges_from(ebunch_to_add, **attr)
        self.update_graph()

    def add_grouped_edge(self, u, v):
        """Add linked edge.

        For mmodel, a group edge (u, v) allows u or v
        to be a list of nodes. A grouped edge represents one or several
        nodes flowing into one node.
        """

        u = [u] if isinstance(u, str) else u
        v = [v] if isinstance(v, str) else v
        edge_list = list(product(u, v))
        self.add_edges_from(edge_list)

    def add_grouped_edges_from(self, group_edges: list):
        """Add edges from grouped values."""

        for u, v in group_edges:
            self.add_grouped_edge(u, v)

    @property
    def grouped_edges(self):
        """Return grouped edges based on the graph."""
        g_edges_reversed = defaultdict(list)

        for u, v in self.edges:
            g_edges_reversed[v].append(u)

        g_edges = defaultdict(list)

        for u, v in g_edges_reversed.items():
            g_edges[tuple(v)].append(u)

        grouped_edges = []
        for k, v in g_edges.items():
            k = k[0] if len(k) == 1 else list(k)
            v = v[0] if len(v) == 1 else v
            grouped_edges.append([k, v])

        return grouped_edges

    def update_graph(self):
        """Update edge attributes based on node objects and edges.

        The edge "output" is not defined if the parent node does not have
        the "output" attribute or the child node does not have the parameter.
        """

        for u, v in self.edges:
            if self.nodes[u] and self.nodes[v]:
                v_sig = self.nodes[v]["signature"].parameters
                if self.nodes[u]["output"] in v_sig:
                    self.edges[u, v]["output"] = self.nodes[u]["output"]
                elif "output" in self.edges[u, v]:  # reset edge output
                    del self.edges[u, v]["output"]

    # graph operations
    def subgraph(self, nodes=None, inputs=None, outputs=None):
        """Extract subgraph by nodes, inputs, and output.

        If multiple parameters are specified, the result is a union
        of the selection. The subgraph is a deep copy of the original graph.
        The behavior is different from the parent class method, where the subgraph
        returns a view of the original graph.
        """

        nodes = nodes or []
        node_inputs = subnodes_by_inputs(self, inputs or [])
        node_outputs = subnodes_by_outputs(self, outputs or [])

        # convert nodes to list because the parent class method accepts generator
        # for nodes.
        # may consider not using the same name as the parent class to avoid collision
        subgraph_nodes = set(list(nodes) + node_inputs + node_outputs)  # unique nodes

        return super().subgraph(subgraph_nodes).deepcopy()

    def replace_subgraph(self, subgraph, node_object):
        """Replace subgraph with a node."""
        return replace_subgraph(self, subgraph, node_object)

    def get_node(self, node):
        """Get node attributes from the graph."""

        return self.nodes[node]

    def get_node_object(self, node):
        """Get node object from the graph."""

        return self.nodes[node]["node_object"]

    def edit_node(self, node, **kwargs):
        """Edit node attributes.
        Returns a new graph.
        """
        node_object = self.nodes[node]["node_object"].edit(**kwargs)

        graph = self.deepcopy()
        graph.set_node_object(node_object)

        return graph

    def visualize(self, outfile=None):
        """Draw the graph.

        Draws the default styled graph.

        :param str outfile: filename to save the graph as. The file extension
            is needed.
        """

        return plain_visualizer(self, str(self), outfile)

    def deepcopy(self):
        """Deepcopy graph.

        The ``graph.copy`` method is a shallow copy. Deepcopy creates a copy for
        the attributes dictionary.
        `graph.copy<https://networkx.org/documentation/stable/reference/classes
        /generated/networkx.Graph.copy.html>_`

        However, for subgraphs, ``deepcopy`` is incredibly inefficient because
        subgraph contains '_graph', which stores the original graph.
        An alternative method is to copy the code from the copy method,
        but use ``deepcopy`` for the items.

        The parser is redefined in the new graph.
        """

        G = self.__class__()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from(
            (u, v, deepcopy(datadict))
            for u, nbrs in self._adj.items()
            for v, datadict in nbrs.items()
        )

        return G
