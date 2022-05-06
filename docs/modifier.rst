Modifier
========

.. autosummary::

    mmodel.modifier

Modifiers are used to modify callables. They are defined as wrappers
(decorators) and they can be stacked. If the modifier requires parameters,
they should be defined before building the model. ``mmodel`` currently
provides two loop modifiers. ``loop_modifier`` takes a single parameter input
and loops that parameter. ``zip_loop_modifier`` takes multiple parameters,
and loops their values pairwise. If the modifier requires parameter input,
it should be defined before supplying to ``Model`` class.

A modifier for ``MModel`` requires to have proper signature defined. To
define the signature, add ``__signature__`` attribute to the wrapped function.
See documentation for `wraps <https://docs.python.org/3/library/functools.html#functools.wraps>`_
and `inspect.signature <https://docs.python.org/3/library/inspect.html?highlight=signature#inspect.signature>`_

When supplying modifiers, the inner modifier should be listed first.

.. Note::
    It is not recommended to use the modifiers as a function decorator. This is
    because modified function requires keyword argument input regardless of its
    an original signature, and it does not provide argument checking (whether an
    input is missing). The behavior is by design. The input parameters are only checked
    once at the model level for performance reasons.

    If necessary, ``signature_binding_modifier()`` can be use to add the binding
    and check steps.

To create a loop for the whole model:

.. code-block:: python

    from mmodel import ModelGraph, MemHandler, modify_node

    def func_a(a, b):
        # returns c
        return a + b

    def func_b(c):
        # returns d
        return c*c

    # model that represents (a + b)(a + b)
    G = ModelGraph(name="example", doc="a example MGraph object")
    G.add_edge("func_a", "func_b")
    G.update_node_object("func_a", func_a, ["c"])
    G.update_node_object("func_b", func_b, ["d"])

    loop_mod = loop_modifier('b')
    model = Model(G, handler=MemHandler, modifier=[loop_mod])

    >>> model(1, [1, 2])
    >>> [4, 9]


:mod:`modifier` module
----------------------

.. autofunction:: mmodel.modifier.loop_modifier
.. autofunction:: mmodel.modifier.zip_loop_modifier
.. autofunction:: mmodel.modifier.signature_modifier
.. autofunction:: mmodel.modifier.signature_binding_modifier
