Modifer and shortcut API
==========================

modifiers
---------

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
For a node, the equivalent function is ``loop_input(parameter)(func)``.
The function signature is modified under the ``loop`` function to indicate that the parameter
requires an iterable input. Under the ``loop_wrapped`` function, the loop parameter is 
isolated, and the function loops over the iterable to create a list result.

Notice that the ``loop_wrapped`` function takes keyword-only arguments. The decision
is made to reduce the overhead of the function call. All modifiers should have
keyword-only arguments.

.. Note::

    *mmodel* requires modifiers to have a proper signature. If the modifier changes the
    function signature, add ``__signature__`` attribute with ``inspect.Signature`` to the
    wrapped function.

    The metadata of the modifier is used to generate the string displayed in the metadata
    at the node and model level. The metadata is a string passed to the "metadata" attribute of
    the modifier function.

shortcuts
-----------

There are not many restrictions of shortcuts. To ensure the same behavior, the shortcut
should take the model as the frist argument and return a new model. It is recommended
to use ``model.edit`` method to create a new model.

To allow the shortcuts to be used in inherited model, make sure to generate new node, graph
and model using the same class as the input model. The class of the input model and graph
can be directly accessed using ``model.__class__`` and ``model.graph.__class__`` or 
type(model) and type(model.graph). The graph carries the information of the node, accessed
by ``model.graph.graph[node_type]``.


See :doc:`modifier and shortcut tutorial </tutorial_modifier>` for how to use modifiers and shortcuts.
See :doc:`modifier reference </ref_modifier>` and :doc:`shortcut reference </ref_shortcut>`
for all available modifiers.
