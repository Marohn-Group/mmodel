Graph 
==============

.. autosummary::

    mmodel.graph.ModelGraph

A directed acyclic graph (DAG) is a directed graph without any cycles.
The model graphs in ``mmodel`` are based on the DAG, where each node represents
an execution step, and each edge represents the data flow from one callable
to another. DAG structure allows us to create model graphs with nonlinear
nodes.

The ``ModelGraph`` class is the main graph class to establish a model graph.
The class inherits from ``networkx.DiGraph``, which is compatible with all
``networkx`` operations
(see `documentation <https://networkx.org/documentation/stable/>`_).

Another benefit of using graphs is that they can be added as a component in
a more complex graph. Again, this increases the reusability of the models.

A graph node is a callable with user-defined attributes. The object of the
nodes can be updated by supplying the node object and the return key of the
callable.

.. code-block:: python

    def func(a, b):
        # returns "c"
        return a + b

    G = ModelGraph()
    G.add_node_object("func", func, ["c"])

A graph edge (u, v) is the link between two callable nodes, with
user-defined attributes:

.. code-block:: python

    def func_a(a, b):
        # returns c
        return a + b

    def func_b(c):
        # returns d
        return c*c

    # model that represents (a + b)(a + b)
    G = ModelGraph(name="example", doc="a example MGraph object")

    G.add_edge("func_a", "func_b")
    G.add_node_object("func_a", func_a, ["c"])
    G.add_node_object("func_b", func_b, ["d"])


:mod:`graph` module
----------------------

.. autoclass:: mmodel.graph.ModelGraph
    :members:
    :show-inheritance:
