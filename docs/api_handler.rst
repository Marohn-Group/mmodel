Handler API
===========

.. autosummary::

    mmodel.handler

Handlers in ``mmodel`` represent different execution methods for the provided
graph. As of ``model 0.3.0``, all handlers are executed in topological order,
inherited from ``TopologicalHandler``.


handler class
--------------

There are three required elements of a handler class/instance:

1. handler should take "graph" and "extra_returns" as two (and only) positional
   arguments
2. handler should define ``__signature__`` with ``inspect.Signature`` object
   to allow signature detection with ``inspect.signature``
3. the resulting handler object should be callable.

Modify the ``Model`` class if these conditions cannot be satisfied.

Inherit ``TopologicalHandler`` abstract class
---------------------------------------------

The instantiation of ``TopologicalHandler`` requires the "graph" 
and "extra_returns" arguments.

``TopologicalHandler`` is an abstract factory class that executes the nodes
in topological order, a linear ordering of the nodes for each directed
edge u -> v, u is ordered ahead of v. 

The call method is defined as the following:

.. code-block:: python

    def __call__(self, **kwargs):
    """Execute graph model by layer"""

    data_instance = self.initiate(**kwargs)

    for node, node_attr in self.order:
        try:
            self.run_node(data_instance, node, node_attr)
        except Exception as e:
            self.raise_node_exception(data_instance, node, node_attr, e)

    return self.finish(data_instance, self.returns)

The following four methods are required:

1. ``initiate``, runs before the execution
2. ``run_node``, execute each node
3. ``raise_node_exception``, exception message for each node
4. ``finish``, runs after all nodes are executed and handles returns as well.
