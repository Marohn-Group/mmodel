Creating a model graph
======================

A directed acyclic graph (DAG) is a directed graph without any cycles.
The model graphs in ``mmodel`` are based on the DAG, where each node represents
an execution step, and each edge represents the data flow from one callable
to another. DAG structure allows us to create model graphs with nonlinear
nodes.

Define a graph
--------------

The ``ModelGraph`` class is the main graph class to establish a model graph.
The class inherits from ``networkx.DiGraph``, which is compatible with all
``networkx`` operations
(see `documentation <https://networkx.org/documentation/stable/>`_).
To create and modify the graph,
see the documentation for adding 
`nodes <https://networkx.org/documentation/stable/tutorial.html#nodes>`_
and adding `edges <https://networkx.org/documentation/stable/tutorial.html#edges>`_

Aside from the ``networkx`` operations,
``mmodel`` provides ``add_grouped_edge`` and ``add_grouped_edges_from`` to add edges.

.. code-block:: python

    from mmodel import ModelGraph
    
    G = ModelGraph()

    G.add_grouped_edge(['a', 'b'], 'c')

    # equivalent to
    # G.add_edge('a', 'b')
    # G.add_edge('a', 'c')

Similarly, with multiple grouped edges

.. code-block:: python

    grouped_edges = [
        (['a', 'b'], 'c'),
        ('c', ['d', 'e']),
    ]

    G = ModelGraph()

    G.add_grouped_edges_from(grouped_edges)
    
    >>> print(G)
    ModelGraph with 5 nodes and 4 edges

Set node objects
-----------------

Each node in the graph represents an execution, and the edges represents the data
flow. Therefore we need to link the node to its execution method. In ``mmodel``
a node object is a combination of:

1. callable, function or function-like ("func")
2. callable return variable names ("returns")
3. callable parameter

For linking the node object to the node, two methods are provided:
``set_node_object`` and ``set_node_objects_from``. 
The latter accepts a list of node objects.

.. code-block:: python
    
    def test_func(a, b):
        return a + b

    G.set_node_object(node='a', func=test_func, returns=['c'])

    # or with multiple node objects
    node_objects = [
        ('a', test_func, ['c']),
        ('b', test_func, ['c']),
    ]

    G.set_node_objects_from(node_objects)

In most cases, only the callable and the returns are needed because the parameters
can be extracted from the function signature. However, there are several cases
the method does not work:

1. python's built-in functions
2. functions without clear signature (``numpy`` universal functions)
3. parameters that are different from defined parameter names

In this cases, "inputs" parameter can be specified, the signature is changed
using the signature modifiers:

.. code-block:: python
    
    import numpy as np
    G.set_node_object(node='b', func=np.sum, returns=['c'], inputs=["a", "b"])

    >>> print(G.view_node('b'))
    b node
      callable: sum(a, b)
      returns: c
      modifiers: [signature_modifier, {'parameters': ['a', 'b']}]

.. Note::
    The object is stored as a node attribute and the function signature
    (`inspect.Signature`) is stored. The parameter values are converted
    to signature objects.

The name of the parameters that pass through each edge is determined and stored
in the edge attribute "val". 

Name and docstring
----------------------

The name and graph string behaves as the networkx graphs. To add name to graph:


.. code-block:: python
    
    # during graph definition
    G = ModelGraph(name="ModelGraph Example")

    # after definition
    # G.graph['name'] = 'ModelGraph Example'

    >>> print(G)
    ModelGraph named 'ModelGraph Example' with 0 nodes and 0 edges

Mutability
------------

The graph object is mutable. A shallow or deepcopy might be needed to create a copy
of the graph.

.. code-block:: python
    
    G.copy() # shallow copy
    G.deepcopy() # deep copy

For more ways to interact with ModelGraph, and networkx.graph see
:doc:`graph reference </ref_graph>`.
