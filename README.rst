MModel
======

|GitHub version| |PyPI version shields.io| |PyPI pyversions| |Unittests|
|Docs|

MModel is a lightweight and modular model-building framework
for small-scale and nonlinear models. The package aims to solve
scientific program prototyping and distribution difficulties, making
it easier to create modular, fast, and user-friendly packages.

Quickstart
----------

To create a nonlinear model that has the result of
`(x + y)log(x + y, base)`:

.. code-block:: python

    from mmodel import ModelGraph, Model, MemHandler
    import math
    import numpy as np

    def func(sum_xy, log_xy):
        """Function that adds a value to the multiplied inputs."""
        return sum_xy * log_xy + 6

The graph is defined using grouped edges (the ``networkx`` syntax of edge
the definition also works.)

.. code-block:: python

    # create graph edges
    grouped_edges = [
        ("add", ["log", "function node"]),
        ("log", "function node"),
    ]

The functions are then added to node attributes. The order of definition
is node_name, node_func, output, input (if different from original function),
and modifiers.

.. code-block:: python

    # define note objects
    node_objects = [
        ("add", np.add, "sum_xy", ["x", "y"]),
        ("log", math.log, "log_xy", ["sum_xy", "log_base"]),
        ("function node", func, "result"),
    ]

    G = ModelGraph(name="example_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

To define the model, the name, graph, and handler need to be specified. Additional
parameters include modifiers, descriptions, and returns lists. The input parameters
of the model are determined based on the node information.

.. code-block:: python

    example_model = Model("example_model", G, handler=(MemHandler, {}), description="Test model.")

The model behaves like a Python function, with additional metadata. The graph can
be plotted using the ``draw`` method.

.. code-block:: python

    >>> print(example_model)
    example_model(log_base, x, y)
    returns: z
    graph: example_graph
    handler: MemHandler()

    Test model.

    >>> example_model(2, 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    30.0

    >>> example_model.draw()

The resulting graph contains the model metadata and detailed node information.

.. .. |br| raw:: html
    
..     <br/>

.. .. image:: example.png
..   :width: 300
..   :alt: example model graph

One key feature of ``mmodel`` that differs from other workflow is modifiers, 
which modify callables post definition. Modifiers work on both the node level
and model level.

Example: Use ``loop_modifier`` on the graph to loop the nodes that require the
"log_base" parameter.

.. code-block:: python 

    from mmodel import loop_modifier

    H = G.subgraph(inputs=["log_base"])
    H.name = "example_subgraph"
    loop_node = Model("submodel", H, handler=(MemHandler, {}))

    looped_G = G.replace_subgraph(
        H,
        "loop_node",
        loop_node,
        output="looped_z",
        modifiers=[(loop_modifier, {"parameter": "log_base"})],
    )
    looped_G.name = "looped_graph"

    looped_model = Model("looped_model", looped_G, loop_node.handler)


We can inspect the loop node as well as the new model.

.. code-block:: python 

    >>> print(loop_node)
    loop_submodel(log_base, sum_xy)
    returns: z
    graph: example_subgraph
    handler: MemHandler()
    modifiers:
      - loop_modifier('log_base')

    >>> print(looped_model)
    looped_model(log_base, x, y)
    returns: looped_z
    graph: looped_graph
    handler: MemHandler()
    
    >>> looped_model([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    [30.0, 18.0]


Use the ``draw`` method to draw the graph. There are three styles
"plain", "short", and "verbose", which differ by the level of detail of the
node information. A graph output is displayed in Jupyter Notebook
or can be saved using the export option.

.. code-block:: python

    G.draw(style="short")
    example_model.draw(style="plain", export="example.pdf") # default to draw_graph

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
installation. For macos systems, sometimes `brew install` results
in unexpected installation path, it is recommended to install
with conda::

    conda install -c conda-forge pygraphviz

To install test and docs, despondencies run::

    pip install .[test] .[docs]

To run the tests in different python environments and cases 
(py38, py39, py310, py311, coverage and docs)::

    tox

To create the documentation, run under the "/docs" directory::

    make html


.. |GitHub version| image:: https://badge.fury.io/gh/peterhs73%2FMModel.svg
   :target: https://github.com/Marohn-Group/mmodel

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/mmodel.svg
   :target: https://pypi.python.org/pypi/mmodel/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/mmodel.svg

.. |Unittests| image:: https://github.com/Marohn-Group/mmodel/actions/workflows/tox.yml/badge.svg
    :target: https://github.com/Marohn-Group/mmodel/actions

.. |Docs| image:: https://img.shields.io/badge/Documentation--brightgreen.svg
    :target: https://github.com/Marohn-Group/mmodel-docs/
