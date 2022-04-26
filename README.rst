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
    
    linked_edges = [
        ("func a", ["func b", "func c"]),
        (["func b", "func"], "func d"),
    ]

    node_objects = [
        ("func a", (func_a, ["sum_xy", "dif_xy"])),
        ("func b", (func_b, ["sum_xyz"])),
        ("func c", (func_c, ["abs_xy"])),
        ("func d", (func_d, ["xyz"])),
    ]

    model_graph = ModelGraph("Example")
    model_graph.add_linked_edges(linked_edges)
    model_graph.update_node_objects_from(node_objects)

    example_func = Model(model_graph, handler=MemExecutor)

    >>> example_func(1, 2, 3)
    >>> 6


To loop a specific parameter. All modification occurs at the model graph
level.

.. code-block:: python

    from mmodel import subgraph_by_parameters, modify_subgraph, basic_loop

    subgraph = subgraph_by_parameters(["z"])
    loop_mod = basic_loop("z")
    loop_node = Model(subgraph, handler=MemExecutor, modifiers=[loop_mod])
    loop_model_graph = modify_subgraph(
        graph, subgraph, "z loop node", loop_node, loop_node.returns
        )

    example_loop_func = Model(loop_model_graph, handler=MemHandler)

    >>> example_loop_func(1, 2, [3, 4])
    >>> [6, 7]

.. To modify a single node

.. .. code-block:: python

..     modify_node(graph, node, modifiers=[])

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
