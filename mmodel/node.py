from mmodel.signature import modify_signature, add_signature, convert_signature
from inspect import signature
import numpy as np
from mmodel.metadata import nodeformatter
from mmodel.utility import construction_dict, modify_func
import types


class Node:
    """A node class that takes case of node operations."""

    _sigless_functype = (np.ufunc, types.BuiltinFunctionType)

    def __init__(self, name, func, inputs=None, output=None, modifiers=None, **kwargs):
        # static
        self.name = name
        self.output = output
        # properties

        self._inputs = inputs or []
        self._modifiers = modifiers or []
        self.func = func  # trigger setter

        self.functype = type(func).__name__
        self.doc = func.__doc__

        self._base_func = self.convert_func(func, self._inputs)
        self._node_func = modify_func(self._base_func, self._modifiers)
        self.__signature__ = signature(self._node_func)

        # kwargs can overwrite properties like doc, functype, etc.
        self.__dict__.update(**kwargs)

    def convert_func(self, func, inputs):
        """Convert function to a node function.

        If the inputs is None, the original signature is changed to
        keyword only. If inputs are provided, the signature is
        changed based on the inputs and keyword only.

        For numpy.ufunc and builtin type, "inputs" value is required.
        """

        if type(func) in self._sigless_functype:
            if not inputs:
                raise Exception(
                    f"node {repr(self.name)} numpy.ufunc type function "
                    "requires 'inputs'"
                )
            func = add_signature(func, inputs)
        elif inputs:
            func = modify_signature(func, inputs)
        else:
            func = convert_signature(func)

        return func

    @property
    def inputs(self):
        """Return a copy of inputs."""
        return self._inputs.copy()

    @property
    def node_func(self):
        """Return node_func."""
        return self._node_func

    @property
    def modifiers(self):
        """Return a copy of modifiers."""
        return self._modifiers.copy()

    @property
    def signature(self):
        """Return signature."""
        return self.__signature__

    def edit(self, **kwargs):
        """Edit node. A new node object is created."""

        con_dict = construction_dict(self, ["inputs", "modifiers"], ["functype", "doc"])

        con_dict.update(kwargs)

        return self.__class__(**con_dict)

    def __call__(self, *arg, **kwargs):
        return self.node_func(*arg, **kwargs)

    def __str__(self):
        return nodeformatter(self)
