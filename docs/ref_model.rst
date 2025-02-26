Model
======

*mmodel* model building favors composition over inheritance.
The ``Model`` class takes several components, namely, graph, handler, and
modifiers. A handler handles the graph calculation and data
flow, and a modifier is a wrapper that applies simple modifications
to the callable. The handler class is passed to the "handler" argument,
and if the handler requires additional arguments, the keyword arguments
can also be passed to the ``Model`` class. The modifier argument
accepts a list of modifier decorators. If the decorators have
arguments, the argument should be applied first.
The resulting ``Model`` instance is a callable that behaves like a function.

The ``Model`` class also provides parameter checking and default value
filling functionality at the ``__call__`` level. Note that handlers
and modifiers require keyword inputs.

:mod:`model` module
----------------------

.. autoclass:: mmodel.model.Model
    :members:
    :show-inheritance:
