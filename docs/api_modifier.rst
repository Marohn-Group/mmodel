Modifier API
=============

.. autosummary::

    mmodel.modifier


Modifiers should be defined the same as closure or decorators. See
documentation for 
`wraps <https://docs.python.org/3/library/functools.html#functools.wraps>`_.
Here is an example of a loop modifier:

.. code-block:: python

    def loop_modifier(func, parameter: str):
        """Loop - iterates one given parameter

        :param list parameter: target parameter to loop
        """

        @wraps(func)
        def loop_wrapped(**kwargs):

            loop_values = kwargs.pop(parameter)
            return [func(**kwargs, **{parameter: value}) for value in loop_values]

        return loop_wrapped


.. Note::
    The wrapped function changes all parameters to keyword only. The behavior is
    intended to reduce overhead during model definition (model changes all parameters
    to positional-or-keyword-arguments).

    For individual functions, if necessary, ``signature_binding_modifier()`` 
    can be used to add the binding and check the steps.

    A modifier for ``MModel`` requires to have proper signature. If the modifier changes the
    function signal, add ``__signature__`` attribute with ``inspect.Signature`` to the wrapped
    function.
