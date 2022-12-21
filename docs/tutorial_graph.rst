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
and adding `edges <https://networkx.org/documentation/stable/tutorial.html#edges>`_.

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
2. callable return variable name ("output")
3. callable parameter ("inputs")

For linking the node object to the node, two methods are provided:
``set_node_object`` and ``set_node_objects_from``. 
The latter accepts a list of node objects. 

.. code-block:: python

    def test_func(a, b):
        return a + b

    G.set_node_object(node='a', func=test_func, output='c')

    >>> print(G.view_node('a'))
    a
      callable: test_func(a, b)
      return: c
      modifiers: []

    # or with multiple node objects
    # both nodes adds input values but outputs in different parameter
    node_objects = [
        ('a', test_func, 'c'),
        ('b', test_func, 'd'),
    ]

    G.set_node_objects_from(node_objects)

    >>> print(G.view_node('b'))
    b
      callable: test_func(a, b)
      return: d
      modifiers: []


.. Note::
    The object is stored as a node attribute and the function signature
    (`inspect.Signature`) is stored. The parameter values are converted
    to signature objects.

The name of the parameters that pass through each edge is determined and stored
in the edge attribute "val". 

.. note::
    
    The note output is a single variable. If the node outputs the multiple variable
    the return tuple is assigned to the defined output variable.

Change function input parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To avoid re-defining functions using different input parameters, the "inputs" parameter
of the ``set_node_object`` can change the node signature. The signature replacement is
a thin wrapper with very small performance overhead. The modification also leaves the
modifier and its parameters in the modifiers section.

.. code-block:: python
    
    def test_func(a, b):
        return a + b

    G.set_node_object(node='a', func=test_func, output='c', inputs=['m', 'n'])

    >>> print(G.view_node('a'))

    a
      callable: test_func(m, n)
      return: c
      modifiers: [signature_modifier, {'parameters': ['m', 'n']}]


.. Note:: 

    The graph variable flows restricts to keyword arguments only for function parameters.
    They can be modified with by changing the inputs of the function, and the modified
    function allows keyword arguments.

Built-in functions and functions without signature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are different types of functions that ``inspect.signature`` cannot extract
the parameters from, namely:

1. python's built-in functions
2. ``numpy`` ufuncs

The wrapper is able to identify the above functions, and replace the signature:

.. code-block:: python

    from operator import add
    G.set_node_object(node='a', func=add, output='c', inputs=["m", "n"])

    >>> print(G.view_node('a'))
    a
      callable: add(m, n)
      return: c
      modifiers: [signature_modifier, {'parameters': ['m', 'n']}]


    import numpy as np
    G.set_node_object(node='b', func=np.sum, output='c', inputs=["m", "n"])

    >>> print(G.view_node('b'))
    b
      callable: sum(m, n)
      return: c
      modifiers: [signature_modifier, {'parameters': ['m', 'n']}]

Function with variable length of arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In mmodel graph, argument length of a node is fixed. For a function with variable
length of arguments, additional arguments can be provided using the input function.


.. code-block:: python

    def test_func_kwargs(a, b, **kwargs):
        return a + b, kwargs

    G.set_node_object(node='a', func=test_func_kwargs, output='c', inputs=["m", "n", "p"])

    >>> print(G.view_node('a'))
    a
      callable: test_func(m, n, p)
      return: c
      modifiers: [signature_modifier, {'parameters': ['m', 'n', 'p']}]

    >>> G.nodes['a']['func'](m=1, n=2, p=4)
    (3, {'p': 4})

Function with default arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For functions with default arguments, the inputs can be shorter than the total number
of parameters.

.. code-block:: python

    def test_func_defaults(m, n, p=2):
        return m + n + p
    
    G.set_node_object(node='a', func=test_func_defaults, output='c', inputs=["m", "n"])

    >>> print(G.view_node('a'))
    a
      callable: test_func_defaults(m, n)
      return: c
      modifiers: [signature_modifier, {'parameters': ['m', 'n']}]
    
    >>> G.nodes['a']['func'](m=1, n=2)
    5

.. Note::

    To avoid performance overhead, signature_modifier modifies the signature in order.
    Currently, it is not possible to replace selected parameters.

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
