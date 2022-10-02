Modifying model and node
=========================

Modifiers are used to modify callables. They can be python closures (wrappers)
or decorators. They are used during the definition of the
node object or the model. A modifier is provided as (func, kwargs) tuple.

To add a loop modifier to the node 'add':

.. code-block:: python

    G = ModelGraph()

    def func_a(a, b):
        # returns "c"
        return a + b

    def func_b(c):
        # returns "d"
        return c*c

    from mmodel import loop_modifier

    G.add_edge('add', 'power')
    # set object without modifiers
    G.set_node_object('power', func_b, ['d'])

    # set object with modifier
    G.set_node_object(
        'add', func_a, ['c'], modifiers=[(loop_modifier, {"parameter": "b"})]
    )

    # post modification
    # a new copy of graph is created
    from mmodel import modify_node
    new_graph = modify_node(G, 'add', modifiers=[(loop_modifier, {"parameter": "b"})])
    
Similarly, use "modifiers" argument to define model modifiers.


Modifier using decorators
-------------------------

If the decorator have additional parameters, the parameters should be applied first.
For example:

.. code-block:: python

    ... modifiers=[(loop_modifier(parameter='b'), {}), ...]
    


Modifier chaining
------------------

Because the modifiers are decorators, they can be chained. The modifiers are
applied from in the list order.

For all available modifiers, see :doc:`modifier reference </ref_modifier>`.
