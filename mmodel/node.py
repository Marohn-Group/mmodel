from mmodel.signature import (
    modify_signature,
    add_signature,
    convert_signature,
    has_signature,
    check_signature
)
from inspect import signature
from mmodel.metadata import nodeformatter
from mmodel.utility import construction_dict, modify_func, parse_functype


class Node:
    """A node class that formats node function and metadata."""

    def __init__(self, name, func, inputs=None, output=None, modifiers=None, **kwargs):
        # static
        self.name = self.__name__ = name
        self.output = output

        self._inputs = inputs or []
        self._modifiers = modifiers or []

        self.func = func
        self.functype = parse_functype(func)
        self.doc = func.__doc__

        self._base_func = self.convert_func(func, self._inputs)
        # allow overwrite
        self.node_func = modify_func(self._base_func, self._modifiers)

        # kwargs can overwrite values like doc, functype, etc.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def __signature__(self):
        """Node signature for inspection."""
        return self.signature

    @property
    def signature(self):
        """Return signature."""
        return signature(self.node_func)

    def convert_func(self, func, inputs):
        """Convert function to a node function.

        For numpy.ufunc and builtin type, "inputs" value is required.

        If inputs are provided, the signature is
        changed based on the inputs and keyword-only.
        If the "inputs" is None, the signature is changed keyword only,
        and the default values are removed.

        The keyword-only design reduced binding overhead during function
        calls, and allow more consistency between node, modifier and model.
        """

        if not has_signature(func):
            if not inputs:
                raise Exception(
                    f"node {repr(self.name)} function "
                    "requires 'inputs' to be specified"
                )
            else:
                func = add_signature(func, inputs)
        elif inputs:
            func = modify_signature(func, inputs)
        elif not check_signature(func):
            func = convert_signature(func)

        return func

    @property
    def inputs(self):
        """Return a copy of inputs."""
        return self._inputs.copy()

    @property
    def modifiers(self):
        """Return a copy of modifiers."""
        return self._modifiers.copy()

    def edit(self, **kwargs):
        """Edit node. A new node object is created."""

        con_dict = construction_dict(
            self, ["inputs", "modifiers"], ["functype", "doc", "node_func"]
        )

        con_dict.update(kwargs)

        return self.__class__(**con_dict)

    def __call__(self, *args, **kwargs):
        """The node function is forced to be keyword argument only."""
        return self.node_func(*args, **kwargs)

    def __str__(self):
        return nodeformatter(self)
