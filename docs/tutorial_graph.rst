Build a model graph
=============================

A directed acyclic graph (DAG) is a directed graph without any cycles.
The model graphs in *mmodel* are based on the DAG, where each node represents
an execution step, and each edge represents the data flow from one callable
to another. DAG structure allows us to create model graphs with nonlinear
nodes.
dDefine a graph
--------------

The ``Graph`` class is the main graph class to establish a model graph.
The class inherits from ``networkx.DiGraph``, which is compatible with all
*NetworkX* operations
(see `documentation <https://networkx.org/documentation/stable/>`_).
To create and modify the graph,
see the documentation for adding 
`nodes <https://networkx.org/documentation/stable/tutorial.html#nodes>`_
and adding `edges <https://networkx.org/documentation/stable/tutorial.html#edges>`_.

Aside from the *NetworkX* operations,
*mmodel* provides ``add_grouped_edge`` and ``add_grouped_edges_from`` to add edges.

.. code-block:: python

    from mmodel import Graph, Node
    
    G = Graph()
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

    G = Graph()
    G.add_grouped_edges_from(grouped_edges)

    >>> G # no name is given
    <mmodel.graph.Graph>

    >>> print(G)
    Graph with 5 nodes and 4 edges


For linking the node object to the node, two methods are provided:
``set_node_object`` and ``set_node_objects_from``. 
The latter accepts a list of node objects. 

.. code-block:: python

    def add(x, y):
        """The sum of x and y."""
        return x + y


    def subtract(x, y):
        """The difference between x and y."""
        return x - y


    def multiply(x, y):
        """The product of x and y."""
        return x * y


    G = Graph()
    G.add_grouped_edge(['a', 'b'], 'c')
    G.set_node_object(Node(name="a", func=add, output="z"))

The node object can be accessed using the ``get_node_object`` method.

.. code-block:: python

    node_a = G.get_node_object("a")

    >>> print(node_a)
    a

    add(x, y)
    return: z
    functype: function

    The sum of x and y.

    # or with multiple node objects
    # both nodes add input values but outputs in different parameter
    node_objects = [
        Node("a", add, output="z"),
        Node("b", subtract, output="m"),
        Node("c", multiply, output="n", inputs=["z", "m"]),
    ]
    G.set_node_objects_from(node_objects)

    >>> node_b = G.get_node_object("b")
    >>> print(node_b)
    b

    subtract(x, y)
    return: m
    functype: function

    The difference between x and y.


The object is stored as a node attribute, and the function signature
(`inspect.Signature`) is stored. The parameter values are converted
to signature objects.

graph Methods
----------------

visualization
~~~~~~~~~~~~~~

The graph can be visualized or saved using the ``visualize`` method.


.. code-block:: python

    G.visualize()

    # or with a filename
    G.visualize(outfile="graph.png")



name and docstring
----------------------

The name and graph string behaves as the *networkx* graphs. To add the name to the graph:


.. code-block:: python
    
    # during graph definition
    G = Graph(name="Graph Example")

    # after definition
    # G.graph['name'] = 'ModelGraph Example'

    >>> G
    <mmodel.graph.Graph 'Graph Example'>

    >>> print(G)
    Graph named 'Graph Example' with 0 nodes and 0 edges

mutability
------------

The graph object is mutable. A shallow or deepcopy might be needed to create a copy
of the graph.

.. code-block:: python
    
    G.copy() # shallow copy
    G.deepcopy() # deep copy

For more ways to interact with ``Graph`` and ``networkx.graph`` see
:doc:`graph reference </ref_graph>`.
