Loop
========

.. autosummary::

    mmodel.modifiers

Modifiers are used to modify callables. They are defined as wrappers (decorators)
and they can be stacked. If the modifier requires parameters, they should be
defined before building the model. ``mmodel`` currently provides two loop modifiers.
``basic_loop`` takes a single parameter input and loops that parameter. ``zip_loop``
takes multiple parameters, and loops their values pairwise.


To create a loop for the whole model:

.. code-block:: python

    from mmodel import ModelGraph, MemHandler, modify_node

    def func_a(a, b):
        return a + b

    def func_b(c):
        return c*c

    G = ModelGraph()
    G.add_edge("func_a", "func_b")
    G.update_node_objects_from(
        [('func a', func_a, ["c"]), ('func b', func_b, ["d"])]
        )

    loop_mod = basic_loop('b')
    model = Model(G, handler=MemHandler, modifier=[loop_mod])

    >>> model(1, [1, 2])
    >>> [4, 9]


:mod:`loop` module
----------------------

.. autofunction:: mmodel.loop.basic_loop
