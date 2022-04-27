Model
=====

.. autosummary::

    mmodel.graph.ModelGraph

``MModel`` model building favors composition over inheritance.
The ``Model`` class takes three components: model_graph, handler, and
modifiers. A handler takes care of the graph calculation and data
flow, and a modifier is a wrapper that applies simple modification
to the callable. The ``Model`` class instance is a callable itself.

If the handler requires additional parameter input (e.g. ``H5Handler``),
the input should be supplied to ``handler_args`` in (key, value) pairs.

``Model`` class also provides parameter checking and default value
filling functionality at the ``__call__`` level. Note that handlers
and modifiers require keyword inputs.

:mod:`model` module
----------------------

.. autoclass:: mmodel.model.Model
    :members:
    :show-inheritance:
