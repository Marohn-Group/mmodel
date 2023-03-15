Modifying model and node
=========================

Modifiers are used to modify callables. They can be python closures (wrappers)
or decorators. They are used during the definition of the
node object or the model. A modifier is provided as ``(func, {kwargs_dict})`` tuple.

To add a loop modifier to the node 'add':

.. code-block:: python

    G = ModelGraph()


    def add(a, b):
        """The sum of a and b."""
        return a + b


    def squared(c):
        """The squared value of c."""
        return c**2


    from mmodel import loop_modifier

    G.add_edge("add", "squared")
    # set object without modifiers
    G.set_node_object("squared", squared, "d")

    # set object with modifier
    G.set_node_object("add", add, "c", modifiers=[(loop_modifier, {"parameter": "b"})])

    # post modification
    # a new copy of the graph is created
    from mmodel import modify_node

    H = modify_node(G, "add", modifiers=[(loop_modifier, {"parameter": "b"})])

Similarly, use "modifiers" argument to define model modifiers.


Modifier using decorators
-------------------------

If the decorator has additional parameters, the parameters should be applied first.
For example:

.. code-block:: python

    ... modifiers=[(loop_modifier(parameter='b'), {}), ...]
    

Modifier chaining
------------------

Because the modifiers are decorators, they can be chained. The modifiers are
applied from in the list order.

For all available modifiers, see :doc:`modifier reference </ref_modifier>`.
