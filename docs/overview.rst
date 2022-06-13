Overview
========

Motivation
-----------

The ``mmodel`` package is developed as a backend for our simulation package
``mrfmsim`` (publishing soon) to tackle some frustrations of the scientific
coding process [1]_, [2]_. Often, public or in-house scientific packages do
not address the varying programming levels among graduate students in a
scientific research group. Due to the nature of graduate students wanting to
focus on the effort of the result, the code written is often lacked quality
and not well tested (unit test or code review). The code review requires a
review of the simulation's scientific model and the code written. Both are
difficult to do, especially for experiments with complex components. For our
complex systems, we often have shared parts, yet they follow nonsequential
execution steps. Because of its complexity, students often simulate experiments
without knowing the underlying experimental model or structure. 

``mmodel`` attempts to help with some of the issues outlined above. ``mmodel``
focuses on building a modular framework, easy to test individual components,
and providing visualization for the complex models. Furthermore, the modular
systems also help with code distribution, as well as introduce different
levels of entrances for the package:

 ======================= =================== 
  action                  programing level   
 ======================= =================== 
  run model               beginner           
  inspect model           beginner           
  create new model        beginner  
  modify model            intermediate       
  create components       intermediate       
  new execution method    advanced           
  code maintenance        advanced           
 ======================= =================== 

How does it work?
-----------------

``mmodel`` uses a directed acyclic graph (DAG) to represent a non-linear
model, with nodes presenting individual functions and edges representing
parameter flow. The graph is created with a custom ``networkx`` graph class
while retaining all of its graph algorithms and methods.

Once the model graph is defined, a build method ``Model`` creates the
executable based on the model graph, graph handler, and additional modifiers.
Constructing a model using a directed graph allows for clear execution steps,
error messages, and easy testing. Notably, we can modify the subgraph easily
without changing the model, which is efficient in terms of performance and
code writing. For example, we can create a loop of the subgraph when looping
the whole model is time-consuming due to matrix operation components outside
of the loop.

Philosophy
-----------

``mmodel`` intends to be the framework that packages build upon, and we follow
some of the fundamental philosophies:

separation of graph model and model execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The graph model and execution steps are separated. This design allows for future
modification and optimization of model execution albeit new software implementation
(parallel) or hardware (GPU, cloud computing) without needing to modify existing
graph.

lightweight
^^^^^^^^^^^
The graph node can be a simple function without any added syntax. All modifiers
are closure decorators with limited overhead to the node or system. The
lightweight nature allows for better performance and easier modification of
the model components. 

prioritize execution performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The most time-consuming components, for example, creating a new model,
and determining execution steps, occurs at import time or model initialization
time. Therefore, the overhead spent on the runtime is as small as possible.

explicit
^^^^^^^^
Since ``mmodel`` is intended as a framework for scientific packages, we want to
make the API and model building process as explicit as possible. See ``mrfmsim``
for some of our high-level design choices.

References
----------

.. [1] Perkel, J. M. How to Fix Your Scientific Coding Errors. Nature 2022, 
   602 (7895), 172–173. https://doi.org/10.1038/d41586-022-00217-0.

.. [2] Strand, J. F. Error Tight: Exercises for Lab Groups to Prevent Research
   Mistakes; preprint; PsyArXiv, 2021. https://doi.org/10.31234/osf.io/rsn5y.
