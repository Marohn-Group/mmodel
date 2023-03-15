Handler
=======

Handler executing in topological order
---------------------------------------

Currently all handler executes in topological order. The handler provides
detailed message when exceptions occur during individual node execution.

.. autosummary::

    mmodel.handler.BasicHandler

``BasicHandler`` executes each node and stores the result in a dictionary. All
intermediate values are preserved in the dictionary.

.. autosummary::

    mmodel.handler.MemHandler
    mmodel.handler.MemData

``MemHandler`` calculates each input parameter usage. Then, the instance
executes each node and stores the result in a custom dictionary ``MemData``. 
The number of times a value is used in the graph is initialized with MemData object.
Each time a key is accessed (used as input for a node), the object calculates the
remaining number. If it is zero (no longer needed for the sequent nodes),
the value of the key is deleted. The behavior has a very small overhead and reduces
peak memory usage.

.. autosummary::

    mmodel.handler.H5Handler
    mmodel.handler.H5Data

``H5Handler`` executes each node and stores the result in an h5 file. For each
node execution, the parameters are read from the h5 file. Each instance call
stores values in the same h5 file, with a subgroup in the format of
"name_time_uuid". The naming scheme makes sure the h5 subgroup entries are
unique for each instance run.

.. note::

    For values that are object type and cannot be stored as H5 database, the string
    of the object is stored as an attribute.

:mod:`handler` module
-----------------------

.. autoclass:: mmodel.handler.TopologicalHandler
    :members:
    :show-inheritance:

.. autoclass:: mmodel.handler.MemHandler
    :members:
    :show-inheritance:

.. autoclass:: mmodel.handler.BasicHandler
    :members:
    :show-inheritance:
    
.. autoclass:: mmodel.handler.H5Handler
    :members:
    :show-inheritance:
