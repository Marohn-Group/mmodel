Graph 
==============

.. autosummary::

    mmodel.graph.MGraph

A directed acyclic graph (DAG) is a directed graph without any cycles.
The model graphs in ``mmodel`` are based on the DAG, where each node represents
an execution step, and each edge represents the data flow from one callable
to another. DAG structure allows us to create model graphs with nonlinear
nodes.

The ``MGraph`` class is the main graph class to establish a model graph.
The class inherits from ``networkx.DiGraph``, which is compatible with all
``networkx`` operations
(see `documentation <https://networkx.org/documentation/stable/>`_).

A graph node is a callable with user-defined attributes:

- ``node_object``: node callable
- ``return_params``: the parameter names for the returned values

.. code-block:: python

    def func(a, b):
        return a + b

    G = MGraph()
    G.add_node("func", node_obj=func, return_params=["c"])

A graph edge (u, v) is the link between two callable nodes, with
user-defined attributes:

- ``interm_params``: the names of the parameters that are passed from
   node u to v. The parameter name should match the input requirement
   of node v.

.. code-block:: python

    def func_a(a, b):
        return a + b

    def func_b(c):
        return c*c

    G = MGraph()
    G.add_node("func_a", node_obj=func_a, return_params=["c"])
    G.add_node("func_b", node_obj=func_b, return_params=["d"])

    G.add_edge("func_a", "func_b", interm_params=["c"])

.. note::

    For ``MGraph``, all nodes in an edge need to be added first.
    The behavior is different from networkx graphs, where the user can
    define the edge without all nodes defined.

:mod:`graph` module
----------------------

.. autoclass:: mmodel.graph.MGraph
    :members:
    :show-inheritance:
