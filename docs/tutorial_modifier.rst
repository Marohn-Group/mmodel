Modify nodes and models
=====================================

Traditionally, to modify a component of a pre-defined model, one has to rewrite the
code. The approach is error-prone and not scalable. *mmodel* uses DAG to create
modular models that allow easy modification of nodes and models post-definition using modifiers. A modifier is a decorator that can modify the function of a node or the model itself.  For example, to add a loop modifier to the node "add":

.. code-block:: python

    from mmodel import Graph, Node
    G = Graph()


    def add(a, b):
        """The sum of a and b."""
        return a + b


    def squared(c):
        """The squared value of c."""
        return c**2


    from mmodel.modifier import loop_input

    G.add_edge("add", "squared")
    # set object without modifiers
    G.set_node_object(Node("squared", squared, "d"))

    # set object with modifier
    G.set_node_object(Node("add", add, "c", modifiers=[loop_input(parameter='b')]))

    # post modification
    # a new copy of the graph is created

    H = G.edit_node("add", modifiers=[loop_input('b')])

Similarly, use the ``modifiers`` argument to define model modifiers.


Modifier chaining
------------------

Because the modifiers are decorators, they can be chained. The modifiers in the
list are applied in the order of the ``modifiers`` argument.

See :doc:`modifier API </api_modifier>` for modifier API,
and `modifier reference </ref_modifier>` for all available modifiers.
