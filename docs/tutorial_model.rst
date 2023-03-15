Building a model
================

The model is built based on the graph and the desired handler. A ``mmodel``
handler is an execution method that handles the node execution order and 
intermediate value flow. The resulting instance is a callable that behaves
like a function. The resulting model copies and freezes the graph, making
it immutable. The handler is given as the (class, kwargs) tuple.

.. code-block:: python

    # see the Graph page on how to build a graph

    from mmodel import MemHandler

    model = Model(G, handler=(MemHandler, {}))

.. Note::

    The graph cannot have isolated nodes or cycles.

The model determines the parameter for the model instance.

Extra return variables
----------------------------

The default return of the model is the output of the terminal nodes. To
output intermediate variables, use "returns" to define additional
output for the model. All other handler parameters can be directly passed
as keyword arguments.

For all available handlers, see :doc:`handler reference </ref_handler>`. 
