Handler
=======

Handler executing in topological order
---------------------------------------

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
