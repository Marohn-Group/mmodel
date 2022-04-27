Overview
========


``MModel`` targets the issue in the science community that simulation is
often not well tested and documented. Furthermore, tests and model distribution
are difficult for models with complex components because it is hard to
figure out the issue during testing. ``MModel`` provides a modular solution
that helps test individual components of a model and package the
model for distribution. 

``MModel`` uses a directed acyclic graph (DAG) to represent a mathematical
model, with nodes presenting individual functions, and edges representing
parameter flow. Once the model graph is defined, a build method ``Model``
creates the executable based on the model graph, graph handler, and
additional modifiers.

The modular nature of ``MModel`` allows for a clear separation of individual
functions. The separation allows for easy testing, function modification,
and subgraph modification. One notable subgraph modification is creating loops
on the fly, which cannot do with an already packaged model. 
Another benefit is that functions and modifiers can be shared
throughout the module, allowing for better testing and upgradeability.
