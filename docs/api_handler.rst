Handler API
===========

Handlers in *mmodel* represent different execution methods for the provided
graph. Currently, all handlers are executed in topological order,
inherited from ``TopologicalHandler``.

Handler class
--------------

There are three required elements of a handler class/instance:

1. The handler should take "graph" and "returns" as two (and only) positional
   arguments.
2. The handler should define ``__signature__`` with ``inspect.Signature`` object
   to allow signature detection with ``inspect.signature``.
3. The resulting handler object should be callable.

Modify the ``Model`` class if these conditions cannot be satisfied.

Handler Data class and TopologicalHandler
------------------------------------------
Handler data stores the input value and all return values of the node execution.
To define a custom handler, a Data class should be defined, 
and it should have `__getitem__` and `__setitem__` methods.
If the Model inherits the TopologicalHandler, the class DataClass should be
defined as the Handler data class.

See :doc:`handler reference </ref_handler>` for the handler reference.
