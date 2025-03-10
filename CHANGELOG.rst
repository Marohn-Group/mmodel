Changelog
========= 
All notable changes to this project will be documented in this file.

The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to
`Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_

[0.8.0] - 2025-02-05
---------------------

Fixed
^^^^^^^

- Fixed the issue that the "node_func" attribute can be overwritten during editing.
- Fixed the issue that the "output" attribute of the edge is not updated during editing.
- Fixed the issue of the different behavior of numpy.ufunc signature due to
  ``inspect.signature`` change in the Python version 3.11.9.
- Rewrite node internal logic for converting function.

Changed
^^^^^^^

- Change the Node class "inputs" behaviors.
    - "inputs" can be used to explicitly define \*arg, and \*\*kwargs by adding "\*" as
      a separator.
- Allow adding grouped edges with two lists. The resulting edges are the
  product of two edges. For example, a grouped edge [[a, b], [c, d]] produces
  four edges (a, c), (a, d), (b, c), and (b, d).
- Change default graph attribute to {graph_module: 'mmodel'}.
- Change instance representation to show names of instance in nodes, graphs, models and model groups.
- Change the "defaults" parameter to "param_defaults" in the Model class to avoid naming collision.

Added
^^^^^

- Add property "grouped_edges" to the Graph class that returns a list of grouped edges.
- Add "modifier" decorator for wrapped modifier functions to provide additional information and metadata.
- Add ``ModelGroup`` class that can group multiple model definition together.
- Add "shortcut" module and two shortcuts ``print_shortcut`` and ``loop_shortcut``.

[0.7.0] - 2024-01-31
-----------------------

Major changes to internal APIs. Only Python >= 3.10 are supported.
The signature binding behavior is rewritten to reduce node overhead.

Changed
^^^^^^^

- Reduce the amount of signature binding behavior to reduce node overhead.
    - The internal function calls are keyword only.
    - The ``Model`` and ``Node`` class instance calls
      can be positional or keyword arguments with proper binding and error
      messages.
- Change Python requirement to 3.10.
- Change ``ModelGraph`` to ``Graph``.
- Change ``draw`` module to ``visualizer`` module.
- - Change node definition to ``Node`` object.
- Change the plotting diagram method to ``visualize`` and use "outfile" to export.
- Custom metadata and plotting are through ``MetadataFormatter``
  and ``Visualizer`` class objects.
- Node function parameters are positional or keyword arguments
  instead of keyword only.
- Default values can only be applied to Model class objects.
- Change Model "description" attribute to "doc".
- ``Node.edit``, ``Graph.edit_node``, ``Model.edit``, and ``Model.edit_node``
  methods to modify and generate new nodes, graphs, and model objects.
- Handler's additional arguments are supplied as a dictionary using
  "handler_kwargs" parameter when instantiating ``Model`` object.
- ``loop_modifier`` adds "_loop" to the function signature parameter.
- Improved node exception messages.
- Change the edge attribute from "var" to "output".
- Change attribute undefined message.

Removed
^^^^^^^

- Remove ``shortcut`` module.

Added
^^^^^

- Add ``node`` module for node definition.
- Add ``signature`` module for function signature operations.
- Add "inputs" length checking during node definition.
- Add ``order`` attribute to the ``Model`` class to show the node execution order.


[0.6.2] - 2023-06-23
--------------------

Changed
^^^^^^^

- ``set_node_object`` accepts additional keyword arguments.
- Allow ``modifier_shortcut`` to change the model name.

[0.6.1] - 2023-4-18
-----------------------

Fixed
^^^^^

- Fix issue #14, where the escaped "\\n" does not display correctly
  in the graphviz dot graph.

[0.6.0] - 2023-4-17
-----------------------

Version 0.6.0 is a major update with a new Model and modifier API.
The new API aims to simplify the model definitions and allow for external
Python decorators.

Changed
^^^^^^^

- The "handler" argument in the Model class takes the handler class, and additional
  parameters are passed to the Model class as keyword arguments.
- The modifiers are now defined as proper decorators to facilitate the
  integration with decorators from other Python libraries.
- The "modifier" argument in the ModelGraph and Model class takes the modifier
  after the argument definition.
- Modifier naming change to simplify the definition.
- Node object definition allows user-defined attributes.

Added
^^^^^

- Add shortcut module.
- Add a lambda parser that attempts to extract lambda function expression.
- Add ``profile_time`` modifier.
- Add metadata parsing ability to modifiers.

[0.5.2] - 2023-3-30
-----------------------

Fixed
^^^^^

- Fix the issue where ``deepcopy`` does not copy the "_parser" attribute.
- Fix the inconsistency of format in metadata when the object doesn't have a name.

Changed
^^^^^^^

- Change the subgraph from a view to a copy of the graph.

[0.5.1] - 2023-3-29
-----------------------

Fixed
^^^^^

- Fix the issue ``modify_node`` doesn't remove the old modifiers.

Changed
^^^^^^^

- Change "executor" to a private Model class attribute ``Model._executor``.
- Change test node functions and docstring for consistency.
- Change the "full" style to "verbose" in metadata and drawing methods.

Added
^^^^^

- Add "order" attribute to the Model class to show the order of the execution.
- Add "metadata" module to format metadata information.
- Add graph information to model metadata.

[0.5.0] - 2023-3-15
------------------------
The package is moved to `Marohn Group <https://github.com/Marohn-Group/mmodel>`_.

API Change
^^^^^^^^^^

- Change graph API where individual nodes can only have a single output.
- Change node attribute "base_func" to "_func".
- Change model attribute "base_graph" to "graph".
- Change edge attribute "val" to "var".
- Change ``view_node`` to ``node_metadata``.
- Change ``util.modify_subgraph`` function to ``util.replace_subgraph``.
- Change ``subgraph_by_parameters`` and ``subgraph_by_returns`` to
  ``subnodes_by_inputs`` and ``subnodes_by_outputs``.
- Change ``model_signature`` and ``model_returns`` to
  ``modelgraph_signature`` and ``modelgraph_returns``
  add both as methods in the graph class.
- Change "returns" to "output". The value should be a string.
- Parameter "returns" is a Model exclusive parameter that denotes the graph output.
- Change ``Model.get_node_object`` to ``Model.get_node_func``, the base function is
  returned.

Fixed
^^^^^

- Fix the issue where modify subgraph cannot add inputs or modifiers.
- Fix the issue in tests that node attributes are not compared in ``graph_equal()``.
- Fix the issue that the original graph freezes when creating a model.
- Fix the inconsistency between node and model metadata.
- Fix the issue that "None" is included in the returns list.

Changed
^^^^^^^^

- Model string output wraps each line at 80 characters.
- ``signature_modifier`` can modify the function with "kwargs".
- Default keyword argument does not show up in the model signature.
- Model's graph checking generates more detailed exception messages.
- Allow isolated graphs in the model (for single-node models).
- The subgraph method of the graph is modified to create a subgraph with
  inputs and outputs.
- ``model.graph`` is a property method. A new copy of the graph is created
  every time.
- Specified inputs are no longer added to the modifier list, and the base function is
  modified.
- Model and graph drawing no longer take method as input. Instead, three style
  options are given, plain, short, and full.

Added
^^^^^^

- Add graph modification when less than graph returns are specified.
- Add ``__name__`` attribute to handler instance.
- ``pos_signature_modifier`` allows for node objects to have positional-only parameters.
- Graph node definition allows for built-in and numpy.ufunc functions.
- Graph node inputs allow default value with a (parameter, default) tuple.
- Add name attribute to Model.
- Add export to graph and model's ``draw`` method.
- Add a "parser" module that parses functions based on different types.
- Add function documentation in metadata.
- Add Python 3.11 testing with tox.

[0.4.0] - 2022-10-3
------------------------

Handler API is rewritten.

Fixed
^^^^^
- Fix object str label alignment, to the left for the graph and model.
- Fix an H5Handler issue that prevents it from writing objects.
- Fix a bug that intermediate nodes output is not included in the final output.

Changed
^^^^^^^
- The ``set_node_object()`` allows for "inputs" parameters for adjusting node
  function input parameters.
- Modifier functions from decorator to closure (both works).
- Modifier list contains the arguments when supplied.
- Handler arguments are supplied with the handler class.
- The draw graph method no longer has a default value.
- Model docstring is tied to the model instead of the graph, use "description"
  for long docstring.
- The 'name' attribute is required for Model instances.
- Include note information in node execute exception.


Added
^^^^^

- Add custom dictionary ``MemData`` as MemHandler's data instance.
- Add custom class ``H5Data`` as H5Handler's data instance.
- Add "returns" parameter to Model.

Removed
^^^^^^^

- The 'info' attribute is no longer used in modifiers and handlers.
- the "model" and "node" are no longer appended to the model and node string output.

[0.3.1] - 2022-06-12
--------------------
Fixed
^^^^^
- Fix duplicated test name.

Added
^^^^^
- Add Github action as the CI tool.

Changed
^^^^^^^
- Node and model string output.
- Change Python minimum requirement to 3.8

[0.3.0] - 2022-06-12
---------------------
Added
^^^^^
- Add ``subgraph_by_returns`` filters graph by node returns.
- Add ``_is_valid_model`` method graph for Model class to validate graph for
  building model executable.
- Add ``draw`` method to ``ModelGraph`` and ``Model`` classes.
- Add ``get_node`` and ``get_node_object`` methods to ``Model`` class.
- Add ``view_node``to ``ModelGraph`` and ``Model`` classes.
- Add ``deepcopy`` method to ``ModelGraph`` because ``graph.copy`` method
  is a shallow copy.

Changed
^^^^^^^
- Move ``subgraph_by_nodes`` and ``subgraph_by_parameters`` to ``filter``
  module
- Change ``Model`` and handlers parameter "model_graph" to "graph".
- Change ``Model`` no longer accept handler arguments (unify behavior of modifiers
  and handlers).
- Change ``Model`` instance str now shows modifier information.
- Modifiers with parameters required to have the "info" attribute set to the
  wrapper (the closure that takes the function as the first parameter). 
  The "info" is used to show the modifier information in the model instance.
- The ``modify_subgraph`` no longer store the subgraph information as a node
  attribute.
- The ``Model._graph`` is a copy of the original graph and is frozen. The same graph
  is used to create the handler object.
- Change graph ``add_node_object`` and ``add_node_objects_from`` to ``set_node_object``
  and ``set_node_object_from``.

Fixed
^^^^^
- Fix ``modify_subgraph`` changes original graph attributes.
- Fix ``ModelGraph`` shares the same class attribute across instances.


[0.2.2] - 2022-05-06
--------------------------
Added
^^^^^
- Add ``modifiers`` input argument to ``ModelGraph.set_node_object``, allowing
  modifiers to be applied to nodes.
- Add ``signature_modifier`` that changes the function signature.
- Add ``signature_binding_modifier`` that adds binding and checking to the wrapped
  function.

[0.2.1] - 2022-05-02
---------------------
Added
^^^^^
- Add ``add_grouped_edges_from`` that adds edges in groups.
- Add ``add_returns`` as additional input to the model. The parameter is used to
  output intermediate values in the returns.
- Add ``tox`` command for different python version test environments: py38,
  py39, coverage, and docs. The latter two check test coverage and build
  sphinx docs.

Changed
^^^^^^^
- Change node attribute ``rts`` to ``returns``.
- Change ``add_linked_edge`` to ``add_grouped_edge``.
- Change ``add_edge`` and ``add_edges_from`` updates graph edge attributes.
- Move ``mmodel`` build method from ``setuptools`` to ``poetry``.

[0.2.0] - 2022-04-27
--------------------

Version 0.2.0 changed the model building from inheritance to composition.
``Model`` class is used to create an executable. 

Added
^^^^^
- Add ``zip_loop_modifier`` modifier that zips multiple arguments for loop.

Changed
^^^^^^^

- Change loop construction to a modifier.
- Change ``MGraph`` to ``ModelGraph``.
- Model graph allows node definition without node object.
- Model graph allows linked edges to simplify graph definition
  with ``add_linked_edges_from``.
- Model graph node attributes do not need to provide.
  key with ``update_node_object`` and ``update_node_objects_from``.

[0.1.1] - 2022-04-06
--------------------
Added
^^^^^
- Add ``doc`` attribute for ``MGraph``.
- Add ``draw_graph()`` method to ``MGraph`` and model classes.
- Add ``__repr__`` for ``MGraph`` and model classes.

Changed
^^^^^^^
- Remove ``name`` input for ``Model`` and ``loop_parameter``.
- Generate model names and looped subgraph names automatically.
- Remove ``title`` input for ``draw_graph``.
- Change model attribute ``graph`` to ``G``, to avoid confusion on the graph's
  inherent attribute ``graph``.
- Separate ``draw_plain_graph()`` and ``draw_graph()``, the former shows
  a simplified version of the graph, and the latter shows all graph details.
- Graph title outputs detailed descriptions of the model instance and
  graph instance.
- Node attribute "return_params" to "returns".
- Edge attribute "interm_params" to "parameters".

[0.1.0] - 2022-04-02
--------------------
Added
^^^^^
- Add class ``MGraph`` for constructing default graphs.
- Add class ``PlainModel`` for constructing callable from graphs.
- Add class ``Model`` for constructing callable from graphs with
  memory management.
- Add class ``H5Model`` for constructing callable from graphs with
  h5 data storage.
- Add function wrapper ``basic_loop`` that creates a basic loop for models.
- Add function ``draw_graph`` for drawing DAG graphs.
