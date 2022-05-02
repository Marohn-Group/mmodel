Handler
=======

Handlers in ``mmodel`` represent different execution methods for the provided
graph. Currently, a handler executes the nodes in topological order, a linear
ordering of the nodes for each directed edge u -> v, u is ordered ahead of v. 
Since the edge represents the data flow. The topological order ensures the
correct execution order.

.. autosummary::

    mmodel.handler.TopologicalHandler

To crate and execute a model:

.. code-block:: python

    from mmodel import ModelGraph, Model, Handler

    def func_a(a, b):
        # returns "c"
        return a + b

    def func_b(c):
        # returns "d"
        return c*c

    # model that represents (a + b)(a + b)
    G = ModelGraph(name="example", doc="a example MGraph object")

    G.add_edge("func_a", "func_b")
    G.add_node_object("func_a", func_a, ["c"])
    G.add_node_object("func_b", func_b, ["d"])

    model = Model(G, handler=PlainHandler)

    >>> model(a=1, b=1)
    >>> 4

The models provided are:

.. autosummary::

    mmodel.handler.MemHandler

``MemHandler`` calculates each input parameter usage. Then, the instance
executes each node and stores the result in a dictionary. After each node
execution, it checks the counter of the input variable. If it is zero (no
longer needed for the sequent nodes), the value is deleted. The behavior has
little overhead and reduces peak memory usage.

.. autosummary::

    mmodel.handler.PlainHandler

``PlainHandler`` executes each node and stores the result in a dictionary. All
intermediate values are preserved in the dictionary.

.. autosummary::

    mmodel.handler.H5Handler

``H5Handler`` executes each node and stores the result in an h5 file. For each
node execution, the parameters are read from the h5 file. Each instance call
stores values in the same h5 file, with a subgroup in the format of
"(instance_id)_(instance_name)_(execution_num)". The naming scheme makes sure
the h5 subgroup entries are unique for each instance run.


:mod:`handler` module
-----------------------

.. autoclass:: mmodel.handler.TopologicalHandler
    :members:
    :show-inheritance:

.. autoclass:: mmodel.handler.MemHandler
    :members:
    :show-inheritance:

.. autoclass:: mmodel.handler.PlainHandler
    :members:
    :show-inheritance:
    
.. autoclass:: mmodel.handler.H5Handler
    :members:
    :show-inheritance:
