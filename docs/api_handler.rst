Handler API
===========

.. autosummary::

    mmodel.handler

Handlers in ``mmodel`` represent different execution methods for the provided
graph. Currently, all handlers are executed in topological order,
inherited from ``TopologicalHandler``.

Handler class
--------------

There are three required elements of a handler class/instance:

1. handler should take "graph" and "returns" as two (and only) positional
   arguments
2. handler should define ``__signature__`` with ``inspect.Signature`` object
   to allow signature detection with ``inspect.signature``
3. the resulting handler object should be callable.

Modify the ``Model`` class if these conditions cannot be satisfied.

Handler Data class and TopologicalHandler
------------------------------------------
Handler data stores the input value and all return values of the node execution.
To define a custom handler a Data class should be defined, 
and it should have `__getitem__` and `__setitem__` method.
If the Model inherits the TopologicalHandler, the class DataClass should be
defined as the Handler data class.
