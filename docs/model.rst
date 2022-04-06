Model
=====

The models in ``mmodel`` represent different execution methods for the provided
graph. All models execute the nodes in topological order, a linear ordering of
the nodes for each directed edge u -> v, u is ordered ahead of v. Since the
edge represents the data flow. The topological order ensures the correct
execution order.

.. autosummary::

    mmodel.model.TopologicalModel

To crate and execute a model:

.. code-block:: python

    def func_a(a, b):
        return a + b

    def func_b(c):
        return c*c

    G = MGraph(name="example", doc="a example MGraph object")
    G.add_node("func_a", node_obj=func_a, returns=["c"])
    G.add_node("func_b", node_obj=func_b, returns=["d"])
    G.add_edge("func_a", "func_b", parameters=["c"])

    model = Model(G)
    # the return should be 4 (parameter "d")
    >>> model(a=1, b=1)
    >>> 4

The models provided are:

.. autosummary::

    mmodel.model.Model

``Model`` instance calculates each input parameter usage. Then, the instance
executes each node and stores the result in a dictionary. After each node
execution, it checks the counter of the input variable. If it is zero (no
longer needed for the sequent nodes), the value is deleted. The behavior has
little overhead and reduces peak memory usage.

.. autosummary::

    mmodel.model.PlainModel

``PlainModel`` executes each node and stores the result in a dictionary. All
intermediate values are preserved in the dictionary.

.. autosummary::

    mmodel.model.H5Model

``H5Model`` executes each node and stores the result in an h5 file. For each
node execution, the parameters are read from the h5 file. Each instance call
stores values in the same h5 file, with a subgroup in the format of
"(instance_id)_(instance_name)_(execution_num)". The naming scheme makes sure
the h5 subgroup entries are unique for each instance run.


:mod:`model` module
--------------------

.. autoclass:: mmodel.model.TopologicalModel
    :members:
    :show-inheritance:

.. autoclass:: mmodel.model.Model
    :members:
    :show-inheritance:

.. autoclass:: mmodel.model.PlainModel
    :members:
    :show-inheritance:
    
.. autoclass:: mmodel.model.H5Model
    :members:
    :show-inheritance:
