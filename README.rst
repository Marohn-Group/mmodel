:author: Peter Sun

MModel
======

``MModel`` is a lightweight and modular model building framework
for small-scale and non-linear models. The package aims to solve the
difficulties in scientific code writing, making it easier to create
a modular package that is fast, easy to test, and user-friendly.

Quickstart
----------

To create a nonlinear model that has the end result of
:math:`|x - y|(x - y + z)`:

.. code-block:: python

    from mmodel import ModelGraph, ModelExecutor, MemHandler

    def func_a(x, y):
        return x + y, x - y
    
    def func_b(sum_xy, z):
        return sum_xy + z
    
    def func_c(dif_xy):
        return abs(dif_xy)
    
    def func_d(sum_xyz, abs_xy):
        return sum_xyz * abs_xy

    # create graph links
    
    grouped_edges = [
        ("func a", ["func b", "func c"]),
        (["func b", "func"], "func d"),
    ]

    node_objects = [
        ("func a", func_a, ["sum_xy", "dif_xy"]),
        ("func b", func_b, ["sum_xyz"]),
        ("func c", func_c, ["abs_xy"]),
        ("func d", func_d, ["result"]),
    ]

    model_graph = ModelGraph("Example")
    model_graph.add_grouped_edges_from(grouped_edges)
    model_graph.add_node_objects_from(node_objects)

    example_func = Model(model_graph, handler=MemExecutor)

    >>> example_func(1, 2, 3)
    >>> 6


To loop a specific parameter. All modification occurs at the model graph
level.

.. note::

    To create a loop for a subgraph requires three steps:  

    1. locate the subgraph with ``subgraph_by_parameters``  
    2. create subgraph model with ``Model`` and loop modifiers  
    3. update graph with the subgraph nodes with ``modify_subgraph``  

.. code-block:: python

    from mmodel import subgraph_by_parameters, modify_subgraph, loop_modifier

    subgraph = subgraph_by_parameters(["z"])
    loop_mod = loop_modifier("z")
    loop_node = Model(subgraph, handler=MemExecutor, modifiers=[loop_mod])
    loop_model_graph = modify_subgraph(
        graph, subgraph, "z loop node", loop_node, loop_node.returns
        )

    example_loop_func = Model(loop_model_graph, handler=MemHandler)

    >>> example_loop_func(1, 2, [3, 4])
    >>> [6, 7]

To modify a single node (add loop to a single node):

.. code-block:: python

    loop_mod = loop_modifier("z")
    modify_node(graph, 'func b', modifiers=[loop_mod])

To draw the graph or the modified model with or without detail

.. code-block:: python

    from mmodel import draw_graph
    
    draw_graph(model_graph, label="Example Figure")

To view the descriptions of the graph and model

.. code-block:: python

    print(model_graph)
    print(example_func)

Installation
------------

Graphviz installation
^^^^^^^^^^^^^^^^^^^^^

To view the graph, Graphviz needs to be installed:
`Graphviz Installation <https://graphviz.org/download/>`_
For windows installation, please choose "add Graphviz to the
system PATH for all users/current user" during the setup.

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^
``mmodel`` uses `poetry <https://python-poetry.org/docs/>`_ as
the build system. The package works with both pip and poetry
installation. 

To install test despondencies run::

    pip install .[test]

(For ``zsh`` shell, run ``pip install ".[test]"``)

To run the tests, run::

    pytest

To run the tests in different python environments (py38 and py39)::

    tox

To install docs despondencies run::

    pip install .[docs]

To make the documentation, run under the "/docs" directory::

    make html 

.. Note::

    To install both test and docs despondencies::
        
        pip install .[test] .[docs]
