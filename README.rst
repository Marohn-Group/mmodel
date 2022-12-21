MModel
======

|GitHub version| |PyPI version shields.io| |PyPI pyversions| |Unittests|
|Docs|

MModel is a lightweight and modular model building framework
for small-scale and nonlinear models. The package aims to solve
scientific program prototyping and distribution difficulties, making
it easier to create modular, fast, and user-friendly packages.
The package is fully tested.

Quickstart
----------

To create a nonlinear model that has the result of
`(x + y)log(x + y, base)`:

.. code-block:: python

    from mmodel import ModelGraph, Model, MemHandler
    import math
    import operator

    def user_func(sum_xy, log_xy):
        """Function that adds a value to the multiplied inputs"""
        return sum_xy * log_xy + 6

The graph is defined using grouped edges (the ``networkx`` syntax of edge
definition also works)

.. code-block:: python

    # create graph edges
    grouped_edges = [
        ("add", ["log", "user func"]),
        ("log", "user func"),
    ]

The functions are then be added to node attributes. The order of definition
is node_name, node_func, output, input (if different from original function),
and modifiers.

.. code-block:: python

    # define note objects
    node_objects = [
        ("add", operator.add, "sum_xy", ['x', 'y']),
        ("log", math.log, "log_xy", ['sum_xy', 'log_base']),
        ("user func", user_func, "result"),
    ]

    graph = ModelGraph(name="example_graph")
    graph.add_grouped_edges_from(grouped_edges)
    graph.set_node_objects_from(node_objects)

To define the model, the name, graph, and handler needs to specified. Additional
parameter include modifiers, description, and returns list. The input parameters
of the model is determined based on the node information.

.. code-block:: python

    example_model = Model("example_model", graph, handler=(MemHandler, {}))

The model behaves like a Python function, with additional metadata. The graph can
be plotted using the ``draw`` method.

.. code-block:: python

    >>> print(example_model)
    example_model(base, x, y)
      signature: 
      returns: result
      handler: MemHandler, {}
      modifiers: none

    >>> example_model(2, 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    30.0

    >>> example_model.draw()

The resulting graph contains the model metadata and detailed node information

.. .. |br| raw:: html
    
..     <br/>

.. .. image:: example.png
..   :width: 300
..   :alt: example model graph

One key feature of ``mmodel`` that differs from other workflow is modifiers, 
which modify callables post definition. Modifiers works on both the node level and model level.

Example: Using modifier and graph to loop the nodes that requires the "log_base" parameter.

.. code-block:: python 

    from mmodel import subgraph_by_parameters, modify_subgraph, loop_modifier

    subgraph = subgraph_by_parameters(graph, ["log_base"])
    loop_node = Model(
        "loop_submodel",
        subgraph,
        handler=(MemHandler, {}),
        modifiers=[(loop_modifier, {"parameter": "log_base"})],
    )
    looped_graph = modify_subgraph(
        graph, subgraph, "loop_node", loop_node, output="looped_result"
    )

    looped_model = Model("loopped_model", looped_graph, loop_node.handler)

We can inspect the loop node as well as the new model

.. code-block:: python 

    >>> print(loop_node)
    loop_submodel(log_base, sum_xy)
      returns: result
      handler: MemHandler, {}
      modifiers: [loop_modifier, {'parameter': 'log_base'}]

    >>> print(looped_model)
    loopped_model(log_base, x, y)
      returns: looped_result
      handler: MemHandler, {}
      modifiers: []
    
    >>> looped_model([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    [30.0, 18.0]


To draw the graph or the underlying graph of the model. Both methods default
to show the detailed node information (``draw_graph`` function). Use ``draw_plain_graph``
only shows node name.

.. code-block:: python

    from mmodel import draw_plain_graph, draw_graph
    graph.draw(method=draw_plain_graph) # default to draw_graph
    example_model.draw(method=draw_plain_graph) # default to draw_graph

Installation
------------

Graphviz installation
^^^^^^^^^^^^^^^^^^^^^

To view the graph, Graphviz needs to be installed:
`Graphviz Installation <https://graphviz.org/download/>`_
For windows installation, please choose "add Graphviz to the
system PATH for all users/current users" during the setup.

MModel installation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    pip install mmodel

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^
MModel uses `poetry <https://python-poetry.org/docs/>`_ as
the build system. The package works with both pip and poetry
installation. 

To install test and docs, despondencies run::

    pip install .[test] .[docs]

To run the tests in different python environments and cases 
(py38, py39, py310, coverage and docs)::

    tox

To create the documentation, run under the "/docs" directory::

    make html


.. |GitHub version| image:: https://badge.fury.io/gh/peterhs73%2FMModel.svg
   :target: https://github.com/peterhs73/MModel

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/mmodel.svg
   :target: https://pypi.python.org/pypi/mmodel/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/mmodel.svg

.. |Unittests| image:: https://github.com/peterhs73/MModel/actions/workflows/tox.yml/badge.svg
    :target: https://github.com/peterhs73/MModel/actions

.. |Docs| image:: https://img.shields.io/badge/Documentation--brightgreen.svg
    :target: https://peterhs73.github.io/mmodel-docs/
