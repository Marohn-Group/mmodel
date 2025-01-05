Use modifiers and shortcuts
=====================================

Traditionally, to modify a component of a pre-defined model, one has to rewrite
the code.
The approach is error-prone and not scalable. *mmodel* uses DAG to create
modular models that allow easy modification of nodes and models post-definition
using modifiers. A modifier is a decorator that can modify the function of a node
or the model itself. To go step further, *mmodel* also provides shortcuts,
that is designed to apply directly to a model.
The shortcuts applies modifiers to the model or nodes in the model.

available modifiers and shortcuts
----------------------------------

.. list-table:: Available modifiers
    :widths: 10 10 90
    :header-rows: 1

    * - Modifier
      - Module
      - Description
    * - :mod:`loop_input <mmodel.modifier.loop_input>`
      - :mod:`mmodel.modifier`
      - Modify function to iterate one given parameter.
    * - :mod:`zip_loop_inputs <mmodel.modifier.zip_loop_inputs>`
      - :mod:`mmodel.modifier`
      - Modify function to iterate the parameters pairwise.
    * - :mod:`profile_time <mmodel.modifier.profile_time>`
      - :mod:`mmodel.modifier`
      - Profile the execution time of a function.
    * - :mod:`print_inputs <mmodel.modifier.print_inputs>`
      - :mod:`mmodel.modifier`
      - Print the inputs of the function with units.
    * - :mod:`print_output <mmodel.modifier.print_output>`
      - :mod:`mmodel.modifier`
      - Print the outputs of the function with units.
    * - :mod:`loop_shortcut <mmodel.shortcut.loop_shortcut>`
      - :mod:`mmodel.shortcut`
      - Loop over a parameter during the experiment execution. 
    * - :mod:`print_shortcut <mmodel.shortcut.print_shortcut>`
      - :mod:`mmodel.shortcut`
      - Apply ``print_inputs`` and ``print_output`` shortcuts to individual nodes
        that print out intermediate variable values during node execution.

apply a modifier to a node or model
-----------------------------------

For example, to add a loop modifier to the node "add":

.. code-block:: python

    from mmodel import Graph, Node
    G = Graph()


    def add(a, b):
        """The sum of a and b."""
        return a + b


    def squared(c):
        """The squared value of c."""
        return c**2


    from mmodel.modifier import loop_input

    G.add_edge("add", "squared")
    # set object without modifiers
    G.set_node_object(Node("squared", squared, "d"))

    # set object with modifier
    G.set_node_object(Node("add", add, "c", modifiers=[loop_input(parameter='b')]))

    # post modification
    # a new copy of the graph is created

    H = G.edit_node("add", modifiers=[loop_input('b')])

Similarly, use the ``modifiers`` argument to define model modifiers.

shortcut usage
--------------

loop shortcut
^^^^^^^^^^^^^

The loop shortcut works by locating the first dependency of the parameter 
in the graph. It then creates a subgraph that contains all the nodes that
depend on the parameter. A new experiment is created with the subgraph as a 
single node, and the node function is an experiment model. When multiple 
parameters need to be looped, the user needs to inspect the order of the 
parameter appearance in the graph to achieve an optimal result.

For example, a graph of :math:`G=\{V=\{A, B, C\}, E=\{(A, B), (B, C)\}\}`::

    A -> B -> C

    A(a, b)
    B(c, d)
    C(e, f)

The optimal way to loop c and e is to define the loop of parameter e in 
node C first and then define the loop of parameter c in node B second. If 
the order given is reversed, both parameters c and e are looped at node B 
level. The reason for the behavior is that when loop c is created, the 
graph::

    A -> BC

    A(a, b)
    BC(c, d, e, f)

As a result, the subsequent loop definition only recognizes the subgraph 
node BC and loop the node instead.

.. note::

    For a two-loop system, the optimal order can always be resolved. 
    However, looping more than three parameters, the optimal order may not 
    be resolved. Therefore, the design decision is made for the user to 
    define the loop order.


print shortcut
^^^^^^^^^^^^^^

The print shortcut aims to print out intermediate values during
node execution to check the execution process. The shortcut is helpful for
slow algorithms and looped models. We also do not want the algorithm to
create unnecessary subgraphs. Therefore, the final design of the shortcut
applies modifiers to individual nodes instead of the entire model. The
design is flexible and works if the underlying graph structure is changed.
The user decides the string format and output style to maintain flexibility.
For the shortcut's unachievable output style, the
users are encouraged to add modifiers to the nodes directly.

For example a graph of :math:`G=\{V=\{A, B, C\}, E=\{(A, B), (B, C)\}\}`::

    A -> B -> C

    def A(a, b):
        c = a + b
        return c

    def B(c, d):
        e = c + d
        return e

    def C(e, f):
        g = e + f
        return g

And the model is ``M = Model(graph=G, ...)``. To output the input value a, 
intermediate value of c and e:

.. code-block:: python

    # M = Model(...)
    >>> print_shortcut(M, ['a={a:.2f}', 'c={c:.2f}', 'e={e:.2f}'])
    >>> M(a=1, b=2, d=4, f=10)
    a=1.00
    c=3.00 
    e=7.00

The shortcut works by applying a ``print_inputs`` modifier and 
``print_output`` modifier to node A, and a ``print_output`` modifier to 
node B.

The shortcuts can modify the print keyword arguments. For example, the
print function's default "end" parameter is "\n". To change the
"end" parameter to " | ":

.. code-block:: python

    # M = Model(...)
    >>> M = print_shortcut(M, ['a={a:.2f}', 'c={c:.2f}', 'e={e:.2f}'], end=' | ')
    >>> M(a=1, b=2, d=4, f=10)
    a=1.00 | c=3.00 | e=7.00 |

However, in a loop, the output stays in a single line, but we want to create
a linebreak for each loop. The user can apply a modifier that has a unique 
"end" parameter to create the line break or use a second shortcut:

.. code-block:: python

    M = print_shortcut(print_shortcut(M, ['a={a:.2f}', 'c={c:.2f}'], end=' | '), ['e={e:.2f}'])

The output for a looped model:

.. code-block:: python

    # M = Model(...)
    >>> M_loop = loop_shortcut(M, 'a')
    >>> M_loop(a_loop=[1, 2], b=2, d=4, f=10)
    a=1.00 | c=3.00 | e=7.00
    a=2.00 | c=4.00 | e=8.00

The decision to have a uniform print parameter argument is to simplify the
user interface and the underlying algorithm. The shortcut is used to apply
the print-related shortcuts quickly. Users are encouraged to create 
additional nodes for monitoring the execution process, which can benefit from 
the ``print_shortcut`` as well.

modifier and shortcut chaining
--------------------------------

Because the modifiers are decorators, they can be chained. The modifiers in the
list are applied in the order of the ``modifiers`` argument. The output of a
shortcut is a model, therefore, we can apply multiple shortcuts to a single model.


See :doc:`modifier and shortcut API reference </api_modifier_shortcut>` for
creating custom modifiers and shortcuts.
See :doc:`modifier reference </ref_modifier>` and :doc:`shortcut reference </ref_shortcut>`
for all available modifiers.
