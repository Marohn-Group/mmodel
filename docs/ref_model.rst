Model
======

``MModel`` model building favors composition over inheritance.
The ``Model`` class takes three components: graph, handler, and
modifiers. A handler takes care of the graph calculation and data
flow, and a modifier is a wrapper that applies simple modifications
to the callable. The handler class is passed to the "handler" argument,
and if the handler requires additional arguments, the keyword arguments
can be passed to the ``Model`` class as well. The modifier argument
accepts a list of modifier decorators. If the decorators have
accepts argument, the argument should be applied first.
The resulting ``Model`` instance is a callable that behaves like a function.

``Model`` class also provides parameter checking and default value
filling functionality at the ``__call__`` level. Note that handlers
and modifiers require keyword inputs.

:mod:`model` module
----------------------

.. autoclass:: mmodel.model.Model
    :members:
    :show-inheritance:
