:author: Peter Sun
:date: 04/5/2022


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
        ("func a", {"node_obj": func_a, "return_params": ["sum_xy", "dif_xy"]}),
        ("func b", {"node_obj": func_b, "return_params": ["sum_xyz"]}),
        ("func c", {"node_obj": func_c, "return_params": ["abs_xy"]}),
        ("func d", {"node_obj": func_d, "return_params": ["xyz"]}),
    ]

    edge_list = [
        ("func a", "func b", {"interm_params": ["sum_xy"]}),
        ("func a", "func c", {"interm_params": ["dif_xy"]}),
        ("func b", "func d", {"interm_params": ["sum_xyz"]}),
        ("func c", "func d", {"interm_params": ["abs_xy"]}),
    ]

    G = MGraph()
    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)

    model = Model(G)
    
    >>> model(1, 2, 3)
    >>> 6


To loop a specific parameter

.. code-block:: python

    model.loop_parameter(param="z")

    >>> model(1, 2, [3, 4])
    >>> [6, 7]

To draw the graph or the modified model with or without detail

.. code-block:: python

    G.draw_graph(show_detail=False)
    model.draw_graph(show_detail=True)


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
