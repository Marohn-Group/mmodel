Modifying model and node
=========================

Modifiers are used to modify callables. They are defined as decorators. 
Here we use decorators to modify already defined callables, namely
the model and nodes in the graph. They are used during the definition of the
node object or the model.

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
    bloop = loop_modifier('b')
    G.set_node_object('add', func_a, ['c'], modifiers=[bloop])

    # post modification
    # a new copy of graph is created
    from mmodel import modify_node
    new_graph = modify_node(G, 'add', modifiers=[bloop])
    
Similarly, use "modifiers" argument to define model modifiers.


Modifier with parameters
-------------------------

If the modifier requires parameters, the parameter should be defined first.
The modifier should take a function as the only parameter.


Modifier chaining
------------------

Because the modifiers are decorators, they can be chained. The modifiers are
applied from in the list order.

For all available modifiers, see :doc:`modifier reference </ref_modifier>`.
