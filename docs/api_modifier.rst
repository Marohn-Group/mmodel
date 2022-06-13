Modifier API
=============

.. autosummary::

    mmodel.modifier


Modifiers should be defined the same as decorators. For exaple, see
documentation for 
`wraps <https://docs.python.org/3/library/functools.html#functools.wraps>`_.
In order for ``mmodel`` to display the information of a wrapper, use ``info`` attribute
to indicate the modifier. Here is an example of a loop modifier:

.. code-block:: python

    def loop_modifier(parameter: str):
        """Basic loop wrapper iterates the parameter from loop

        :param list parameter: target parameter to loop
        """

        def wrapper(func):
            @wraps(func)
            def loop_wrapped(**kwargs):

                loop_values = kwargs.pop(parameter)
                return [func(**kwargs, **{parameter: value}) for value in loop_values]

            return loop_wrapped

        # define the wrapper information for  
        wrapper.info = f"loop_modifier({parameter})"

        return wrapper

.. Note::
    It is not recommended to use the modifiers as a decorator during the
    function definition because the modified function requires keyword
    argument input regardless of its original signature, and it does not
    provide argument checking (whether an input argument is missing). 
    The behavior is by design. The input parameters are only checked
    once at the model level for performance reasons.

    If necessary, ``signature_binding_modifier()`` can be used to add the binding
    and check the steps.

A modifier for ``MModel`` requires to have proper signature. If the modifier changes the
function signal, add ``__signature__`` attribute with ``inspect.Signature`` to the wrapped
function.
