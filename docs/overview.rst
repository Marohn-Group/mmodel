Overview
========

Motivation
-----------

The *mmodel* package is developed as a backend for our simulation package
`mrfmsim <https://marohn-group.github.io/mrfmsim-docs/>`_ 
to tackle some frustrations of the scientific
coding process [1]_, [2]_. Often, public or in-house scientific packages do
not address the varying programming levels among graduate students in a
scientific research group. Due to the nature of graduate students wanting to
focus on the effort of the result, the code written is often lacks quality
and not well tested (unit test or code review). The code review requires a
review of the simulation's scientific model and the code written. Both are
difficult to do, especially for experiments with complex components. For our
complex systems, we often have shared parts, yet they follow non-sequential
execution steps. Because of its complexity, students often simulate experiments
without knowing the underlying experimental model or structure. 

*mmodel* attempts to help with some of the issues outlined above. *mmodel*
focuses on building a modular framework, easy-to-test individual components,
and providing visualization for complex models. 

How does it work?
-----------------

*mmodel* uses a two-stage system to construct a Python callable
that behaves like a Python function --- **graph and model**.

The **graph** is a directed acyclic graph (DAG) to represent a non-linear
the procedure, with nodes presenting individual functions and edges representing
parameter flow. The graph is created with a custom *NetworkX* graph class
while retaining all of its graph algorithms and methods. The class ``Graph``
handles the graph construction.

The **model** can be created given the graph, the graph handler, and the modifiers.
The model is a Python executable object that behaves like a Python function.
Specifically, the handler creates the workflow that executes each node, and modifiers
are Python wrappers (closure/decorators) that can modify the nodes and the graph.
The class ``Model`` handles the model construction. Constructing a model using a
directed graph allows for clear execution steps, error messages, and easy testing.
Notably, we can modify the subgraph easily without changing the model, 
which is efficient in terms of performance and code writing. 
For example, we can create a loop of the subgraph when looping the whole model is
time-consuming due to matrix operation components outside of the loop.

Philosophy
-----------

*mmodel* intends to be the framework that packages build upon, and we follow
some of the fundamental philosophies:

Separation of graph model and model execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The graph model and execution steps are separated. This design allows for future
modification and optimization of model execution, albeit new software implementation
(parallel) or hardware (GPU, cloud computing) without needing to modify existing
graph.

Lightweight
^^^^^^^^^^^
The graph node can be a simple function without any added syntax. All modifiers
are closure decorators with limited overhead to the node or system. The
lightweight nature allows for better performance and easier modification of
the model components. 

Prioritize execution performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The most time-consuming components, for example, creating a new model
and determining execution steps, occur at import or model initialization times. 
Therefore, the overhead spent on the runtime is as small as possible.

Explicit
^^^^^^^^
Since *mmodel* is intended as a framework for scientific packages, we want to
make the API and model-building process as explicit as possible. See 
`mrfmsim <https://marohn-group.github.io/mrfmsim-docs/>`_ for some of our
high-level design choices.

References
----------

.. [1] Perkel, J. M. How to Fix Your Scientific Coding Errors. Nature 2022, 
   602 (7895), 172-173. https://doi.org/10.1038/d41586-022-00217-0.

.. [2] Strand, J. F. Error Tight: Exercises for Lab Groups to Prevent Research
   Mistakes; preprint; PsyArXiv, 2021. https://doi.org/10.31234/osf.io/rsn5y.
