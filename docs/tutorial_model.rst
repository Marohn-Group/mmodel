Create a model
======================

The model is built based on the graph and the desired handler. A *mmodel*
handler is an execution method that handles the node execution order and 
intermediate value flow. The resulting instance is a callable that behaves
like a function. The resulting model copies and freezes the graph, making
it immutable. A handler class is passed to the ``handler`` argument, and
any additional arguments of the handler can be passed as a dictionary to
the ``handler_kwargs`` argument.

First, we define the nodes and the graph.

.. code-block:: python

    import numpy as np
    import math
    from mmodel import Graph, Node

    grouped_edges = [
        ("add", ["log", "func node"]),
        ("log", "func node"),
    ]

    def func(sum_xy, log_xy):
        """Function that adds a value to the multiplied inputs."""

        return sum_xy * log_xy + 6

    # define note objects
    node_objects = [
        Node("add", np.add, inputs=["x", "y"], output="sum_xy"),
        Node("log", math.log, inputs=["sum_xy", "log_base"], output="log_xy"),
        Node("func node", func, output="result"),
    ]

    G = Graph(name="example_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

Then, we create the model instance.

.. code-block:: python

    from mmodel import MemHandler

    model = Model(name='model', graph=G, handler=MemHandler, doc="Test model.")

    >>> model
    <mmodel.model.Model 'model'>

    >>> print(model)
    model(log_base, x, y)
    returns: result
    graph: example_graph
    handler: MemHandler

    Test model.

    # visualize the graph
    >>> model.visualize()

.. Note::

    The graph cannot have cycles.

The model determines the parameter for the model instance.

Edit the model
----------------

The model can be edited by appling one or multiple change of the arguments.
For example if we want to change the documentation of the model, we can
use the ``edit`` method. A new model instance is returned.

.. code-block:: python

    new_model = model.edit(doc="New documentation.")

    >>> print(new_model)
    model(log_base, x, y)
    returns: result
    graph: example_graph
    handler: MemHandler

    New documentation.


Extra return variables
----------------------------

The default return of the model is the output of the terminal nodes. To
output intermediate variables, use "returns" to define additional
output for the model. All other handler parameters can be directly passed
as keyword arguments.

See :doc:`handler reference </ref_handler>` for all available handlers. 
