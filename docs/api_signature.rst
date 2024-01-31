Signature API
=================

One of the key features of *mmodel* that differs from other workflow libraries
is the ability to handle signatures. A signature is the set of input 
parameters of a callable. The signature handling in *mmodel* closely 
resembles the signature handling in the Python standard library modules.
As a result, the syntax of running models has a very low entry barrier
and allows minimal code change to use existing Python functions as nodes.

Signature handling and binding
-------------------------------

We can inspect the signature of a callable using the ``inspect`` module.
We can also change the function signature with the module by assigning
a new signature to the function's ``__signature__`` attribute. All nodes
in a *mmodel* graph can be defined using ``Node`` object, and all function
signatures are converted to positional-or-keyword arguments. Additionally,
users can supply inputs to modify the underlying function signature.

.. code:: python

    from mmodel import Node

    def foo(a, b, /):
        return a + b

    node1 = Node('foo', foo)
    node2 = Node('foo', foo, inputs=['d', 'e'])
    
    >>> print(node1)
    foo

    foo(a, b)
    return: c
    functype: function

    >>> print(node2)
    foo

    foo(d, e)
    return: f
    functype: function
    
In the above example, function ``foo`` has two positional-only arguments.
The resulting ``node1`` adjusts the signature to have two 
positional-or-keyword arguments, and ``node2`` changes the signature to 
arguments with different names. The conversion is helpful for built-in 
functions that have only positional-only arguments, and *NumPy*'s ``ufunc`` 
that do not show proper signatures.

We can execute the node with keyword arguments.

.. code:: python

    >>> node1(1, b=2)
    3

    >>> node2(d=3, e=2)
    5

Executing nodes and models directly as callable also shows proper error
messages with incorrect inputs.

.. code:: python

    >>> node2(1, 2, 3)
    TypeError: too many positional arguments

    >>> node2(1, 2. c=3)
    TypeError: got an unexpected keyword argument 'c'

    >>> node2(1)
    TypeError: missing a required argument: 'e'

.. Note::

    These argument checking and error messages are archived by using ``inspect`` 
    module in the ``__call__`` method for both ``Node`` and ``Model`` modules. 
    However, to reduce the overhead, the internal handling of the parameters is 
    keyword only. Internally, ``node.node_func`` is used to execute the node, and
    ``model.model_func`` is used to execute the model. The handling of the
    parameter flow relies on the ``Handler`` class. Therefore, direct execution
    of the ``node_func`` and ``model_func`` does not track the input parameters
    correctly by design.
