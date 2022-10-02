Modifying a subgraph
=====================

Filtering subgraph
--------------------

There are three methods provided for creating a subgraph from the graph:

1. ``subgraph_by_nodes``, filter by nodes
2. ``subgraph_by_parameters``, filter by node callable parameters
3. ``subgraph_by_returns``, filter by node callable returns

.. Note::
    
    The filtered subgraph is a view of the original graph and they are
    frozen.

The resulting subgraph can be built into models:

.. code-block:: python

    H = subgraph_by_returns(G, ['c'])
    model = Model(H, (MemHandler, {}))
 
The filtering is useful if we only want to create model executable for
only part of the graph.

Subgraph as model
------------------

Subgraphing is also useful if we want to apply modifiers to part of the
graph. For example, we want to loop a variable that only part of the subgraph
uses. Here we loop the "base" parameter from the Quickstart example.

.. code-block:: python

    from mmodel import subgraph_by_parameters, modify_subgraph, loop_modifier

    subgraph = subgraph_by_parameters(graph, ["base"])
    loop_node = Model(
        "loop_node",
        subgraph,
        (MemHandler, {}),
        modifiers=[(loop_modifier, {"parameter": "base"})],
    )
    looped_graph = modify_subgraph(graph, subgraph, "loop node", loop_node)
    looped_model = Model("loop_model", looped_graph, loop_node.handler)

.. note::

    The process above: 

    1. filter the graph with ``subgraph_by_parameters``
    2. create subgraph model with ``Model`` and loop modifiers  
    3. update graph with the subgraph nodes object ``loop_node`` with
       ``modify_subgraph``, in this step the original returns list is retained.
       (to modify the returns, use "subgraph_returns" argument)
    4. build the model for the graph with ``Model``. The handler is the same as
       the loop_node.
