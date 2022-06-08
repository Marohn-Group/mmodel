:author: Peter Sun

MModel
======

``MModel`` is a lightweight and modular model building framework
for small-scale and non-linear models. The package aims to solve the
difficulties in scientific program prototyping and distribution, making
it easier to create modular, fast, and user-friendly packages.

Quickstart
----------

To create a nonlinear model that has the end result of
:math:`(x + y)log(x + y, z)`:

.. code-block:: python

    from mmodel import ModelGraph, Model, MemHandler
    import math

    def func_a(x, y):
        return x + y

    def func_b(sum_xy, base):
        return math.log(sum_xy, base)

    def func_c(sum_xy, log_xy):
        return sum_xy * log_xy

    # create graph links

    grouped_edges = [
        ("func a", ["func b", "func c"]),
        ("func b", "func c"),
    ]

    node_objects = [
        ("func a", func_a, ["sum_xy"]),
        ("func b", func_b, ["log_xy"]),
        ("func c", func_c, ["result"]),
    ]

    graph = ModelGraph(name="Example")
    graph.add_grouped_edges_from(grouped_edges)
    graph.add_node_objects_from(node_objects)

    example_func = Model(graph, handler=MemHandler)

    >>> print(example_func)
    Example model
      signature: base, x, y
      returns: result
      handler: MemHandler
      modifiers: none

    >>> example_func(2, 5, 3) # (5 + 3)log(5 + 3, 2)
    24.0

The resulting `example_func` is a callable.

One key feature of ``mmodel`` is modifiers, which modifies callables post
definition. To loop the "base" parameter

.. code-block:: python

    from mmodel import subgraph_by_parameters, modify_subgraph, loop_modifier

    subgraph = subgraph_by_parameters(graph, ["base"])
    loop_node = Model(subgraph, MemHandler, [loop_modifier("base")])
    looped_graph = modify_subgraph(graph, subgraph, "loop node", loop_node)
    looped_func = Model(looped_graph, handler=MemHandler)

    >>> print(looped_func)
    Example model
      signature: base, x, y
      returns: result
      handler: MemHandler
      modifiers: none
    
    >>> looped_func([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2)
    [24.0, 12.0]

.. note::

    To create a loop for a subgraph requires three steps:  

    1. locate the subgraph with ``subgraph_by_parameters``  
    2. create subgraph model with ``Model`` and loop modifiers  
    3. update graph with the subgraph nodes with ``modify_subgraph``  

Modifiers can also be added to the whole model or a single node.

To draw the graph or the underlying graph of the model

.. code-block:: python
    
    graph.draw()
    example_func.draw()

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
