Define a node
=============================

Each node in the graph represents an execution, and the edges represent the data
flow. Therefore, we need to link the node to its execution method. In *mmodel*
a node object is defined by the ``Node`` class. The class takes the following
arguments:


1. ""name", string: node name
2. "func", callable: node function, or function-like
3. "inputs", list: input parameter list (optional)
4. "output", string: return variable name (defaults to None)
5. "modifiers", list: list of modifiers
6. "doc", string: node docstring (optional)

The resulting node object can be executed directly.

.. code-block:: python
    
    def add(a, b):
        """Sum of x and y."""
        return a + b

    node_a = Node("a", func=add, inputs=["m", "n"], output="z")

    >>> node_a
    <mmodel.node.Node 'a'>

    >>> print(node_a)
    a

    add(m, n)
    return: z
    functype: function

    Sum of x and y.

    >>> node_a(m=1, n=2)
    3

remapping function parameter signature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To avoid re-defining functions using different input parameters or for functions
that only allow positional arguments (built-in functions and numpy.ufunc), the
"inputs" parameter can change the node signature.
The signature modification uses a thin wrapper with a very small performance overhead.
The signature change only occurs at the node level. The original function is
not affected.

In a *mmodel* node, the parameter signature needs to be explicitly defined.
For a function with a variable length of arguments, the ``inputs`` parameter
is used to re-define the function signature.

The "*" symbol is used to separate the positional arguments from the keyword-only arguments.
For variable positional parameters, attach the parameters after the positional-or-keyword
arguments and for keyword-only parameters, attach the parameters after the keyword-only
arguments. Parameters with default values can be ignored based on the number of parameter inputs.
Default values are not allowed at the node level. The default value can be defined at the model
level or a custom function should be defined.

.. list-table:: *mmodel* argument modifications
    :widths: 12 12 12 16
    :header-rows: 1

    * - function signature
      - target signature
      - ``inputs`` argument
      - parameter mapping
    * - foo(a, b, \*, c, d)
      - foo(a, b, \*, c, d)
      - N/A
      - a -> a, b -> b, c -> c, d -> d
    * - foo(a, b, \*, c, d=2)
      - foo(a, b, \*, c)
      - ["a", "b", "*", "c"]
      - a -> a, b -> b, c -> c, d -> 2
    * - foo(a, b, \*args, c, d=2)
      - foo(x, y, z, o, \*, p, q)
      - ["a", "b", "\*", "args", "c"]
      - a -> x, b -> y, args -> (z, o), c -> p, d -> q
    * - foo(a, b, \*args, c, d=2, \*\*kwargs)
      - foo(x, y, z, o, \*, p, q, s, t)
      - ["x", "y", "z", "o", "\*", "p", "q", "s", "t"]
      - a -> x, b -> y, args -> (z, o), c -> p, d -> q, kwargs -> (s, t)


.. code-block:: python

    def test_func_kwargs(a, b, **kwargs):
        """Test function."""
        return a + b, kwargs


    node_a = Node("a", func=test_func_kwargs, output="z", inputs=["m", "n", "*", "p"])


    >>> print(node_a)
    a

    test_func_kwargs(m, n, *, p)
    return: z
    functype: function

    Test function.

    >>> node_a(m=1, n=2, p=4)
    (3, {'p': 4})



built-in functions and functions without signature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are different types of functions that ``inspect.signature`` cannot extract
the parameters from, namely:

1. python's built-in functions
2. *NumPy* ufuncs

*mmodel* can identify the above functions and replace the signature:

.. code-block:: python

    from operator import add

    node_a = Node("a", func=add, output="z", inputs=["m", "n"])

    import numpy as np

    node_b = Node("b", func=np.sum, output="d", inputs=["m", "n"])


    >>> print(node_a)
    a

    add(m, n)
    return: z
    functype: builtin_function_or_method

    Same as a + b.


    >>> print(node_b)
    b

    sum(m, n)
    return: d
    functype: numpy._ArrayFunctionDispatcher

    Sum of array elements over a given axis.

The ``Node`` class also accepts additional keyword arguments. For example,
the user can override the function docstring using the "doc" argument.

edit a node
----------------

The node can be edited by applying one or multiple changes to the arguments.
A new node instance is returned.

.. code-block:: python

    def add(a, b):
        """Sum of x and y."""
        return a + b

    node_a = Node("a", func=add, inputs=["m", "n"], output="z")

    # edit the node
    node_a_new = node_a.edit(inputs=["x", "y"], output="w")

    >>> print(node_a_new)
    a

    add(x, y)
    return: w
    functype: function

    Sum of x and y.
