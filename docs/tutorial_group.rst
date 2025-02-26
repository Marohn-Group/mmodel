Create a model group
=====================

In the *mmodel* design, we intend to keep the graph behavior
similar to the *NetworkX* graph. Therefore, all the nodes and edges
are used in the final graph. However, there are cases that graphs
and models shares the similar pool of nodes but different edges.

In this case, a model group can be created to store multiple similar
graphs and models in a single object. The parameters used in the ``ModelGroup``
class are:

1. "name", string: model group name
2. "node_objects", list: list of node objects
3. "model_recipes", dict: dictionary of model recipes, the keys are the model names
4. "model_defaults", dict: shared model parameters between different models
5. "doc", string: model group documentation

.. code-block:: python
    :force:

    from mmodel import Node, ModelGroup, MemHandler
    import numpy as np
    import math

    # define note objects
    node_objects = [
        Node("add", np.add, inputs=["x", "y"], output="sum_xy"),
        Node("log", math.log, inputs=["sum_xy", "log_base"], output="log_xy"),
        Node("sub", np.subtract, inputs=["sum_xy", "log_xy"], output="sub_xy"),
        Node("mul", np.multiply, inputs=["sum_xy", "log_xy"], output="mul_xy"),
    ]

    # create graph edges
    grouped_edges_A = [
        ("add", ["log", "sub"]),
        ("log", "sub"),
    ]

    grouped_edges_B = [
        ("add", ["log", "mul"]),
        ("log", "mul"),
    ]

    model_recipes = {
        "model_A": {"grouped_edges": grouped_edges_A},
        "model_B": {"grouped_edges": grouped_edges_B},
    }

    model_defaults = {"handler": MemHandler}
    model_group = ModelGroup(
        "example_model_group",
        node_objects,
        model_recipes,
        model_defaults,
        doc="Test model group.",
    )

    >>> model_group
    <mmodel.model.ModelGroup 'example_model_group'>

    >>> print(model_group)
    example_model_group
    models: ['model_A', 'model_B']
    nodes: ['add', 'log', 'sub', 'mul']
    model_defaults:
    - handler: <class 'mmodel.handler.MemHandler'>

    Test model group.

The models can be extracted and executed.

.. code-block:: python

    model_A = model_group.models["model_A"]
    model_B = model_group.models["model_B"]

    >>> model_A
    <mmodel.model.Model 'model_A'>

    >>> print(model_A)
    model_A(log_base, x, y)
    returns: sub_xy
    group: example_model_group
    graph: model_A_graph
    handler: MemHandler

    >>> model_A(2, 5, 3)
    5.0

    >>> model_B(2, 3, 4)
    24.0

edit the model group
--------------------

The model group can be edited by applying one or multiple changes to the arguments.
A new model group instance is returned.

.. code-block:: python
    :force:

    new_model_group = model_group.edit(doc="New documentation.")

    >>> print(new_model_group)
    example_model_group
    models: ['model_A', 'model_B']
    nodes: ['add', 'log', 'sub', 'mul']
    model_defaults:
    - handler: <class 'mmodel.handler.MemHandler'>

    New documentation.
