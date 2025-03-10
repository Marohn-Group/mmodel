mmodel
======

|GitHub version| |PyPI version shields.io| |PyPI pyversions| |Unittests|
|DOI|

*mmodel* is a lightweight and modular model-building framework
for small-scale and nonlinear models. The package aims to solve
scientific program prototyping and distribution difficulties, making
it easier to create modular, fast, and user-friendly packages.

For using *mmodel* in a complex scientific workflow, please refer to
the `mrfmsim <https://marohn-group.github.io/mrfmsim-docs/overview.html>`__
on how *mmodel* improves the development of magnetic resonance force
microscopy (MRFM) experiments.

Quickstart
----------

To create a nonlinear model that has the result of
`(x + y)log(x + y, base)`:

.. code-block:: python

    import math
    import numpy as np

    def func(sum_xy, log_xy):
        """Function that adds a value to the multiplied inputs."""

        return sum_xy * log_xy + 6

The graph is defined using grouped edges (the *NetworkX* syntax of edge
the definition also works.)

.. code-block:: python

    from mmodel import Graph, Model, Node, MemHandler
    # create graph edges
    grouped_edges = [
        ("add", ["log", "function node"]),
        ("log", "function node"),
    ]

To add node objects to each node we can use the ``add_node`` method from
the *NetworkX* graph class. *mmodel* provides a way to add a node object to
each node with the ``Node`` class. The class takes the node name, function,
positional inputs, keyword inputs, output, and modifiers as arguments.

Partically, the positional inputs and keyword inputs are used to replace
the original function inputs if necessary. The inputs are given as lists.

The node object can be added to the graph using the ``set_node_object``. The
``set_node_objects_from`` method is used for multiple nodes.

.. code-block:: python

    # define note objects
    node_objects = [
        Node("add", np.add, inputs=["x", "y"], output="sum_xy"),
        Node("log", math.log, inputs=["sum_xy", "log_base"], output="log_xy"),
        Node("function node", func, output="result"),
    ]

    G = Graph(name="example_graph")
    G.add_grouped_edges_from(grouped_edges)
    G.set_node_objects_from(node_objects)

To define the model, the name, graph, and handler need to be specified. Additional
parameters include modifiers, descriptions, and returns lists. The input parameters
of the model are determined based on the node function parameter signature,
or custom signature can be provides using the ``inputs`` parameter. 

.. code-block:: python

    example_model = Model("example_model", G, handler=MemHandler, doc="Test model.")

The model behaves like a Python function with additional metadata. The graph can
be plotted using the ``visualize`` method.

.. code-block:: python

    # model representation
    >>> example_model
    <mmodel.model.Model 'example_model'>

    >>> print(example_model)
    example_model(log_base, x, y)
    returns: result
    graph: example_graph
    handler: MemHandler

    Test model.

    >>> example_model(2, 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    30.0

    >>> example_model.visualize()

The resulting graph contains the model metadata and detailed node information.

.. .. |br| raw:: html
    
..     <br/>

.. .. image:: example.png
..   :width: 300
..   :alt: example model graph

One key feature of ``mmodel`` that differs from other workflows is modifiers, 
which modify callables post-definition. Modifiers work on both the node level
and model level.

Example: Use ``loop_input`` modifier on the graph to loop the nodes that require the
"log_base" parameter.

.. code-block:: python 

    from mmodel.modifier import loop_input

    H = G.subgraph(inputs=["log_base"])
    H.name = "example_subgraph"
    loop_node = Model("submodel", H, handler=MemHandler)

    looped_G = G.replace_subgraph(
        H,
        Node("loop_node", loop_node, output="looped_z", modifiers=[loop_input("log_base")]),
    )
    looped_G.name = "looped_graph"

    looped_model = Model("looped_model", looped_G, loop_node.handler)

    >>> print(looped_model)
    looped_model(log_base, x, y)
    returns: looped_z
    graph: looped_graph
    handler: MemHandler
    
    >>> print(looped_model.get_node_object("loop_node"))
    loop_node

    submodel(log_base, sum_xy)
    return: looped_z
    functype: mmodel.model.Model
    modifiers:
    - loop_input(parameter='log_base')

    >>> looped_model([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    [30.0, 18.0]

The above process is included in the ``shortcut`` module and we can use the
``loop_shortcut`` to directly apply the above process. Note that the shortcut
changes the input parameter name to ``(name)_loop`` to distinguish
between the models.

.. code-block:: python

    from mmodel.shortcut import loop_shortcut
    looped_model = loop_shortcut(example_model, "log_base", name="looped_model")

    >>> print(looped_model)
    looped_model(log_base_loop, x, y)
    returns: result
    graph: example_graph
    handler: MemHandler

    Test model.

    >>> looped_model([2, 4], 5, 3) # (5 + 3)log(5 + 3, 2) + 6
    [30.0, 18.0]

We can use the ``visualize`` method to draw the graph. For a graph, a simple diagram
with only node names shown, and for a model, the diagram shows detailed
node and model information. Customized plotting objects can be created
using the Visualizer class.


.. code-block:: python

    G.visualize()
    # draw the graph and output to a pdf file
    example_model.visualize(outfile="example.pdf")

Installation
------------

Graphviz installation
^^^^^^^^^^^^^^^^^^^^^

To view the graph, Graphviz needs to be installed:
`Graphviz Installation <https://graphviz.org/download/>`_
For Windows installation, please choose "add Graphviz to the
system PATH for all users/current users" during the setup.

For macOS systems, sometimes `brew install` results
in an unexpected installation path, it is recommended to install
with conda::

    conda install -c conda-forge pygraphviz

MModel installation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    pip install mmodel

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^
MModel uses `poetry <https://python-poetry.org/docs/>`_ as
the build system. The package works with both pip and poetry
installation.

To install dependencies for "test" and "docs"::

    pip install .[test] .[docs]

To run the tests in different Python environments and cases 
(py310, py311, coverage and docs)::

    tox

To create the documentation, run under the "/docs" directory::

    make html

Citing *mmdoel*
^^^^^^^^^^^^^^^^^^
The work was `published <https://pubs.aip.org/aip/jcp/article/159/4/
044801/2904249/mmodel-A-workflow-framework-to-accelerate-the>`_ in the Journal 
of Chemical Physics. 

BibTex::

    @article{Sun2023jul,
      title = {mmodel: A Workflow Framework to Accelerate the Development of Experimental Simulations},
      author = {Sun, Peter and Marohn, John A.},
      year = {2023},
      month = {Jul},
      journal = {The Journal of Chemical Physics},
      volume = {159},
      number = {4},
      pages = {044801},
      doi = {10.1063/5.0155617},
      url = {https://pubs.aip.org/jcp/article/159/4/044801/2904249/mmodel-A-workflow-framework-to-accelerate-the}
    }


.. |GitHub version| image:: https://badge.fury.io/gh/peterhs73%2FMModel.svg
   :target: https://github.com/Marohn-Group/mmodel

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/mmodel.svg
   :target: https://pypi.python.org/pypi/mmodel/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/mmodel.svg

.. |Unittests| image:: https://github.com/Marohn-Group/mmodel/actions/workflows/tox.yml/badge.svg
    :target: https://github.com/Marohn-Group/mmodel/actions

.. |Docs| image:: https://img.shields.io/badge/Documentation--brightgreen.svg
    :target: https://github.com/Marohn-Group/mmodel-docs/

.. |DOI| image:: https://img.shields.io/badge/DOI-10.1063/5.0155617-blue.svg
    :target: https://doi.org/10.1063/5.0155617
