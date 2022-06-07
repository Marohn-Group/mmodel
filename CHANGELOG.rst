Changelog
========= 
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_

[Unrealeased]
------------------
Added
^^^^^
- ``subgraph_by_returns`` filters graph by node returns
- ``is_valid_model`` method graph for Model class to validate graph for building model executable
- ``partial_handler`` that creates class with partial parameters defined
- ``draw`` method to ``ModelGraph`` and ``Model`` classes
- add ``get_node`` and ``get_node_object`` methods to ``Model`` class
- add ``view_node``to ``ModelGraph`` and ``Model`` classes

Changed
^^^^^^^
- move ``subgraph_by_nodes`` and ``subgraph_by_parameters`` to ``filter`` module
- ``Model`` and handlers parameter "model_graph" to "graph"
- ``Model`` no longer accept handler arguments (unify behavior of modifiers and handlers)
- ``Model`` instance str now shows modifier information
- modifiers with parameters requires to have "info" attribute set to the wrapper 
  (the closure that takes func as a parameter). The "info" is used to show the modifier information
  in model instance
- ``modify_subgraph`` no longer store the subgraph information as a node attribute


[0.2.2] - 2022-05-06
--------------------------
Added
^^^^^
- add ``modifiers`` input argument to ``ModelGraph.add_node_object``, allowing
  modifiers to be applied to nodes
- add ``signature_modifier`` that changes function signature
- add ``signature_binding_modifier`` that adds binding and checking to wrapped
  function

[0.2.1] - 2022-05-02
---------------------
Added
^^^^^
- add ``add_grouped_edges_from``
- add ``add_returns`` as additional input to model. The parameter is used to
  output intermediate values in the returns.
- add ``tox`` command for different python version test environments: py38, py39,
  coverage, and docs. The latter two checks test coverage and build sphinx docs.

Changed
^^^^^^^
- node attribute ``rts`` to ``returns``.
- ``add_linked_edge`` to ``add_grouped_edge``
- ``add_edge`` and ``add_edges_from`` updates graph edge attributes
- move ``mmodel`` build method from ``setuptools`` to ``poetry``

[0.2.0] - 2022-04-27
--------------------

Version 0.2.0 changed the model building from inheritance to composition.
``Model`` class is used to create executable. 

Added
^^^^^
- add ``zip_loop_modifier`` modifier that zips multiple arguments for loop

Changed
^^^^^^^
- API for creating executable
- loop construction changed as a modifier
- ``MGraph`` to ``ModelGraph``
- model graph allows node definition without node object
- model graph allows linked edges to simplify graph definition
  with ``add_linked_edges_from``
- model graph node attributes does not need to provide
  key with ``update_node_object`` and ``update_node_objects_from``

[0.1.1] - 2022-04-06
--------------------
Added
^^^^^
- ``doc`` attribute for ``MGraph``
- ``draw_graph()`` method to ``MGraph`` and model classes
- ``__repr__`` for ``MGraph`` and model classes

Changed
^^^^^^^
- remove ``name`` input for ``Model`` and ``loop_parameter``
- generate model names and looped subgraph name automatically
- remove ``title`` input for ``draw_graph``
- change model attribute ``graph`` to ``G``, to avoid confusion of the graph's
  inherent attribute ``graph``
- separate ``draw_plain_graph()`` and ``draw_graph()``, the former shows
  a simplified version of graph and latter shows all graph details
- graph title outputs detailed descriptions of the model instance and
  graph instance
- change node attribute "return_params" to "returns"
- change edge attribute "interm_params" to "parameters"

[0.1.0] - 2022-04-02
--------------------
Added
^^^^^
- class ``MGraph`` for constructing default graphs
- class ``PlainModel`` for constructing executable from graphs
- class ``Model`` for constructing executable from graphs with
  memory management
- class ``H5Model`` for constructing executable from graphs with
  h5 data storage
- function wrapper ``basic_loop`` that creates basic loop for models
- function ``draw_graph`` for drawing DAG graphs
