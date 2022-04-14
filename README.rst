:author: Peter Sun
:date: 04/6/2022


MModel
======

``MModel`` is a lightweight and modular model building framework
for small-scale and non-linear models. The package aims to solve the
difficulties in scientific code writing, making it easier to create
a modular package that is fast, easy to test, and user-friendly.

Quickstart
----------

To create a nonlinear model:

.. code-block:: python

    from mmodel import MGraph, Model

    def func_a(x, y):
        return x + y, x - y
    
    def func_b(sum_xy, z):
        return sum_xy + z
    
    def func_c(dif_xy):
        return abs(dif_xy)
    
    def func_d(sum_xyz, abs_xy):
        return sum_xyz * abs_xy

    node_list = [
        ("func a", {"node_obj": func_a, "returns": ["sum_xy", "dif_xy"]}),
        ("func b", {"node_obj": func_b, "returns": ["sum_xyz"]}),
        ("func c", {"node_obj": func_c, "returns": ["abs_xy"]}),
        ("func d", {"node_obj": func_d, "returns": ["xyz"]}),
    ]

    edge_list = [
        ("func a", "func b", {"parameters": ["sum_xy"]}),
        ("func a", "func c", {"parameters": ["dif_xy"]}),
        ("func b", "func d", {"parameters": ["sum_xyz"]}),
        ("func c", "func d", {"parameters": ["abs_xy"]}),
    ]

    G = MGraph("Example graph")
    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    model = Model(G)
    
    >>> model(1, 2, 3)
    >>> 6


To loop a specific parameter

.. code-block:: python

    model.loop_parameter(parameters=["z"])

    >>> model(1, 2, [3, 4])
    >>> [6, 7]

To draw the graph or the modified model with or without detail

.. code-block:: python

    G.draw_graph(show_detail=False)
    model.draw_graph(show_detail=True)

To view the descriptions of the graph and model

.. code-block:: python

    print(G)
    print(model)


Installation
------------


Graphviz installation
^^^^^^^^^^^^^^^^^^^^^^

To view the graph, Graphviz needs to be installed:
`Graphviz Installation <https://graphviz.org/download/>`_
For windows installation, please choose "add Graphviz to the
system PATH for all users/current user" during the setup.

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^

To install run::

    pip install .[test]

(For ``zsh`` shell, run ``pip install ".[test]"``)

To run the tests, run::

    pytest

To make the documentation, run under the "/docs" directory::

    make html 
