Model
======

``MModel`` model building favors composition over inheritance.
The ``Model`` class takes three components: graph, handler, and
modifiers. A handler takes care of the graph calculation and data
flow, and a modifier is a wrapper that applies simple modification
to the callable. For each handler and modifier, a tuple of (class, kwargs)
or (func, kwargs) should be supplied.
The resulting ``Model`` instance is a callable that behaves like a function.

``Model`` class also provides parameter checking and default value
filling functionality at the ``__call__`` level. Note that handlers
and modifiers require keyword inputs.

:mod:`model` module
----------------------

.. autoclass:: mmodel.model.Model
    :members:
    :show-inheritance:
