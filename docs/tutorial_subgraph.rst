Create and modify a subgraph
===============================

The graph used in the tutorial is defined as follows:

.. code-block:: python

    import numpy as np
    import math
    from mmodel import Graph, Node

    grouped_edges = [
        ("add", ["log", "function node"]),
        ("log", "function node"),
    ]

    # define note objects
    node_objects = [
        Node("add", np.add, inputs=["x", "y"], output="sum_xy"),
        Node("log", math.log, inputs=["sum_xy", "log_base"], output="log_xy"),
        Node("function node", func, output="result"),
    ]

    G = Graph(name="example_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

create a subgraph
--------------------------------

There are three methods provided for creating a subgraph from the graph:

1. filter by nodes ("nodes")
2. filter by node callable parameters ("inputs")
3. filter by node callable returns ("outputs")

.. Note::

    The filtered subgraph is a view of the original graph, and they are
    frozen (immutable).

If we filter the graph by the output "log_xy", the node "function node" is
excluded.
The resulting subgraph can be built into models (the graph is defined the same as
README.rst):

.. code-block:: python

    H = G.subgraph(outputs=["log_xy"])
    model = Model("model", H, MemHandler)

    >>> print(H.nodes)
    ['add', 'log']
 
The filtering is useful if we only want to create a model callable for
only part of the graph.

Create a model based on a subgraph
-----------------------------------

Subgraphing is also helpful if we apply modifiers to part of the
graph. For example, we want to loop a variable that only part of the subgraph
uses. Here, we loop the "log_base" parameter from the README example.
The ``replace_subgraph`` function outputs a new graph.

.. code-block:: python 

    H = G.subgraph(inputs=["log_base"])
    loop_node = Model(
        "loop_submodel",
        H,
        handler=MemHandler,
        modifiers=[loop_input("log_base")],
    )
    looped_graph = G.replace_subgraph(H, Node("loop_node", loop_node, output="looped_z"))
    looped_model = Model("looped_model", looped_graph, loop_node.handler)

    >>> print(looped_model)

    looped_model(log_base_loop, x, y)
    returns: looped_z
    graph: example_graph
    handler: MemHandler

The steps are:

1. Filter the graph with ``G.subgraph(inputs=...)``.
2. Create a subgraph model with ``Model`` and loop modifiers.
3. Update the graph with the subgraph nodes object ``loop_node`` with
   ``replace_subgraph``. Use "output" to specify the output name of the subgraph node.
4. Build the model for the graph with ``Model``. The handler is the same as
   the loop_node.

The above process can be replaced with the ``loop_shortcut``.
