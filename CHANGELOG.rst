Changelog
========= 
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_

[unreleased]
--------------------
Added
^^^^^
- ``doc`` attribute for ``MGraph``

Changed
^^^^^^^
- remove ``name`` input for ``Model`` and ``loop_parameter``
- generate model names and looped subgraph name automatically
- remove ``title`` input for ``draw_graph``
- change model attribute ``graph`` to ``G``, to avoid confusion of the graph's
  inherent attribute ``graph``


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
