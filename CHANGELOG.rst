Changelog
========= 
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_

[0.2.0] - 2022-04-27
--------------------

Version 0.2.0 changed the model building from inheritence to composition.
``Model`` class is used to create executable. 

Added
^^^^^
- add ``zip_loop`` wrapper

Changed
^^^^^^^
- API for creating executable
- loop construction changed as a modifier
- ``MGraph`` to ``ModelGraph``
- model graph allows node defintion without node object
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
