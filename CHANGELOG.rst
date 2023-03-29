Changelog
========= 
All notable changes to this project will be documented in this file.

The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to
`Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_

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
- Fix the issue in tests that node attributes are not compared in `graph_equal()`.
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
- Add "__name__" attribute to handler instance.
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

- Add custom dictionary `MemData`` as MemHandler's data instance.
- Add custom class `H5Data` as H5Handler's data instance.
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
