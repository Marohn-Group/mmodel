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

    graph = ModelGraph(name="example_graph")
    graph.add_grouped_edges_from(grouped_edges)
    graph.set_node_objects_from(node_objects)

    example_model = Model("example_model", graph, handler=(MemHandler, {}))

    >>> print(example_model)
    example_model(base, x, y)
      signature: 
      returns: result
      handler: MemHandler, {}
      modifiers: none

    >>> example_model(2, 5, 3) # (5 + 3)log(5 + 3, 2)
    24.0

The resulting ``example_func`` is callable.

One key feature of ``mmodel`` is modifiers, which modify callables post
definition. To loop the "base" parameter.

.. code-block:: python 

    from mmodel import subgraph_by_parameters, modify_subgraph, loop_modifier

    subgraph = subgraph_by_parameters(graph, ["base"])
    loop_node = Model(
        "loop_node",
        subgraph,
        (MemHandler, {}),
        modifiers=[(loop_modifier, {"parameter": "base"})],
    )
    looped_graph = modify_subgraph(graph, subgraph, "loop node", loop_node)
    looped_model = Model("loop_model", looped_graph, loop_node.handler)

    >>> print(looped_model)
    loop_model(base, x, y)
        returns: result
        handler: MemHandler, {}
        modifiers: []
    
    >>> looped_model([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2)
    [24.0, 12.0]


Modifiers can also be added to the whole model or a single node.

To draw the graph or the underlying graph of the model:

.. code-block:: python

    from mmodel import draw_plain_graph
    graph.draw(method=draw_plain_graph)
    example_model.draw(method=draw_plain_graph)

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
