Modifier API
=============

The modifiers are defined as decorator functions that can modify a function
and take additional input parameters. See
documentation for 
`functools.wraps <https://docs.python.org/3/library/functools.html#functools.wraps>`_.
The modifiers can be applied to a node or a model. It is important to note that the
modifier only sees the function rather than the node object, meaning modifiers do not
have access to the node information. The decision is made to simplify the modifier
definition. Modifying the function does not require the modifiers to handle
the passing down of the node information properly, increasing the compatibility
of chained modifiers. 

Here is an example of a loop modifier:

.. code-block:: python

    def loop_input(parameter: str):
        """Modify function to iterate one given parameter.

        :param list parameter: target parameter to loop
            The target parameter name is changed to f"{param}_loop"
        """

        def loop(func):
            param_list = []
            for param in signature(func).parameters.values():
                if param.name == parameter:
                    param_list.append(Parameter(f"{param}_loop", kind=1))
                else:
                    param_list.append(param)

            new_sig = Signature(param_list)

            @wraps(func)
            def loop_wrapped(**kwargs):
                """Isolate the loop parameter and loop over the values."""
                loop_values = kwargs.pop(f"{parameter}_loop")

                return [func(**kwargs, **{parameter: value}) for value in loop_values]

            loop_wrapped.__signature__ = new_sig
            return loop_wrapped

        loop.metadata = f"loop_input({repr(parameter)})"
        return loop

The modifier takes an additional argument "parameter" and returns a modified function.
For a node, the equivalent function is :code:``loop_input(parameter)(func)``.
The function signature is modified under the ``loop`` function to indicate that the parameter
requires an iterable input. Under the ``loop_wrapped`` function, the loop parameter is 
isolated, and the function loops over the iterable to create a list result.

Notice that the ``loop_wrapped`` function takes keyword-only arguments. The decision
is made to reduce the overhead of the function call. All nodes in the Model are supplied
with keyword-only arguments. See :doc:`signature API </api_signature>` for more information.

.. Note::

    *mmodel* requires modifiers to have a proper signature. If the modifier changes the
    function signature, add ``__signature__`` attribute with ``inspect.Signature`` to the
    wrapped function.

    The metadata of the modifier is used to generate the string displayed in the metadata
    at the node and model level. The metadata is a string passed to the "metadata" attribute of
    the modifier function.

See :doc:`modifier tutorial </tutorial_modifier>` for how to use modifiers,
and `modifier reference </ref_modifier>` for all available modifiers.
