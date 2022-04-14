Loop
========

.. autosummary::

    mmodel.loop.basic_loop

One of the main features of ``mmodel`` is the easy creation of loops. For a
target loop parameter, the model group the nodes and their children that
require the parameter as input to a subgraph. Looping only the subgraph allows
for more efficient loop execution.

To create a loop:


.. code-block:: python

    def func_a(a, b):
        return a + b

    def func_b(c):
        return c*c

    G = MGraph()
    G.add_node("func_a", node_obj=func_a, returns=["c"])
    G.add_node("func_b", node_obj=func_b, returns=["d"])
    G.add_edge("func_a", "func_b", parameters=["c"])

    model = Model(G)
    model.loop_parameter(parameters=["b"], method=basic_loop)

    >>> model(1, [1, 2])
    >>> [4, 9]

The ``loop_method`` should be a wrapper that takes a callable and the loop
params as input. The ``basic_loop`` loops the parameters in order.

:mod:`loop` module
----------------------

.. autofunction:: mmodel.loop.basic_loop
