import networkx as nx
from mmodel.draw import draw_graph
from copy import deepcopy
from mmodel.filter import subnodes_by_inputs, subnodes_by_outputs
from mmodel.utility import (
    modelgraph_signature,
    modelgraph_returns,
    replace_subgraph,
    modify_node,
    parse_modifiers,
    content_wrap,
)
from mmodel.parser import parser_engine


class ModelGraph(nx.DiGraph):

    """Create model graphs.

    ModelGraph inherits from `networkx.DiGraph()`, which has all `DiGraph`
    methods.

    The class adds the "type" attribute to the graph attribute. The factory method
    returns a copy of the dictionary. It is equivalent to
    ``{"type": "ModelGraph"}.copy()`` when called.

    The additional graph operations are added:
    - add_grouped_edges and set_node_objects.
    - Method ``add_grouped_edges``, cannot have both edges list.
    - Method ``set_node_object`` updates nodes with the node callable "func" and output.
    - The method adds callable signature 'sig' to the node attribute.
    """

    graph_attr_dict_factory = {"type": "ModelGraph"}.copy

    def __init__(self, *args, parser=parser_engine, **kwargs):
        super().__init__(*args, **kwargs)
        self._parser = parser

    def set_node_object(
        self,
        node,
        func,
        output: str = None,
        inputs: list = None,
        modifiers: list = None,
    ):
        """Add or update the functions of an existing node.

        In the end, the edge attributes are re-determined
        Modifiers are applied directly onto the node. The parser checks the
        function type and returns (at least) three dictionary entries:
        _func, functype, doc.
        """

        node_dict = self.nodes[node]

        modifiers = modifiers or list()
        attr_dict = self._parser(node, func, output, inputs, modifiers)
        node_dict.update(attr_dict)

        self.update_graph()

    def set_node_objects_from(self, node_objects: list):
        """Update the functions of existing nodes.

        The method is the same as adding a node object.
        """

        for node_obj in node_objects:
            # unzipping works for input with or without modifiers
            self.set_node_object(*node_obj)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """Modify add_edge to update the edge attribute in the end."""

        super().add_edge(u_of_edge, v_of_edge, **attr)
        self.update_graph()

    def add_edges_from(self, ebunch_to_add, **attr):
        """Modify add_edges_from to update the edge attributes."""

        super().add_edges_from(ebunch_to_add, **attr)
        self.update_graph()

    def add_grouped_edge(self, u, v):
        """Add linked edge

        For mmodel, a group edge (u, v) allows u or v
        to be a list of nodes. Represents several nodes
        flowing into one node or the other way around.
        """

        if isinstance(u, list) and isinstance(v, list):
            raise Exception("only one edge node can be a list")

        # use add edges from to run less update graph
        # currently a compromise
        if isinstance(u, list):
            self.add_edges_from([(_u, v) for _u in u])
        elif isinstance(v, list):
            self.add_edges_from([(u, _v) for _v in v])
        else:  # neither is a list
            self.add_edge(u, v)

    def add_grouped_edges_from(self, group_edges: list):
        """Add edges from grouped values."""

        for u, v in group_edges:
            self.add_grouped_edge(u, v)

    def update_graph(self):
        """Update edge attributes based on node objects and edges."""

        for u, v in self.edges:
            # the edge "var" is not defined if the parent node does not
            # have "output" attribute, or the child node does not have
            # the parameter

            # extract the parameter dictionary
            v_sig = getattr(self.nodes[v].get("sig", None), "parameters", {})
            if "output" in self.nodes[u] and self.nodes[u]["output"] in v_sig:
                self.edges[u, v]["var"] = self.nodes[u]["output"]

    def node_metadata(self, node: str, full=True, wrap_width=80):
        """Printout node metadata.

        The metadata includes the node information and the node function
        information. If the node is a ``mmodel.Model`` instance; outputs its metadata.
        """

        node_dict = self.nodes[node]

        metadata_list = [
            node,
            "",
            f"{node_dict['func'].__name__}{node_dict['sig']}",
            f"return: {node_dict['output']}",
        ]

        if full:  # adds functype, modifiers, and docs
            metadata_list.append(f"functype: {node_dict['functype']}")
            metadata_list.extend(parse_modifiers(node_dict["modifiers"]))
            doc = node_dict["doc"] or ""
            metadata_list.extend(["", doc])

        wrapped_list = content_wrap(metadata_list, width=wrap_width)

        return "\n".join(wrapped_list).rstrip()

    # graph properties
    @property
    def signature(self):
        """Graph signature.

        :rtype: inspect.Signature object
        """
        return modelgraph_signature(self)

    @property
    def returns(self):
        """Graph returns.

        :rtype: list
        """
        return modelgraph_returns(self)

    # graph operations
    def subgraph(self, nodes=None, inputs=None, outputs=None):
        """Extract subgraph by nodes, inputs, and output.

        If multiple parameters are specified, the result is a union
        of the selection.
        """

        nodes = nodes or []
        node_inputs = subnodes_by_inputs(self, inputs or [])
        node_outputs = subnodes_by_outputs(self, outputs or [])

        # convert nodes to list because the parent class method accepts generator
        # for nodes.
        # may consider not using the same name as the parent class to avoid collision
        subgraph_nodes = set(list(nodes) + node_inputs + node_outputs)  # unique nodes

        return super().subgraph(subgraph_nodes)

    def replace_subgraph(
        self, subgraph, name, func, output=None, inputs=None, modifiers=None
    ):
        """Replace subgraph with a node"""
        return replace_subgraph(self, subgraph, name, func, output, inputs, modifiers)

    def modify_node(
        self, node, func=None, output=None, inputs=None, modifiers=None, inplace=False
    ):
        """Modify node attributes"""
        return modify_node(self, node, func, output, inputs, modifiers, inplace)

    def draw(self, style="full", export=None, wrap_width=30):
        """Draw the graph.

        Draws the default styled graph.

        :param str style: there are three styles, plain, short and full.
            Plain shows nodes only, short shows part of the metadata, and
            long shows all the metadata.
        :param str export: filename to save the graph as. The file extension
            is needed.

        """

        return draw_graph(self, str(self), style, export, wrap_width)

    def deepcopy(self):
        """Deepcopy graph.

        The graph.copy method is a shallow copy. Deepcopy creates copy for the
        attributes dictionary.
        `graph.copy<https://networkx.org/documentation/stable/reference/classes
        /generated/networkx.Graph.copy.html>_`

        However, for subgraphs, deepcopy is incredibly inefficient because
        subgraph contains '_graph', which stores the original graph.
        An alternative method is to copy the code from the copy method,
        but use deepcopy for the items.
        """
        # return deepcopy(self)

        G = self.__class__()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from(
            (u, v, deepcopy(datadict))
            for u, nbrs in self._adj.items()
            for v, datadict in nbrs.items()
        )

        return G
