from mmodel.signature import (
    modify_signature,
    add_signature,
    convert_signature,
    has_signature,
    check_signature,
)
from inspect import signature
from mmodel.metadata import nodeformatter
from mmodel.utility import construction_dict, modify_func, parse_functype
from mmodel.model import Model
import numpy as np


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
        self._node_func = modify_func(self._base_func, self._modifiers)

        # kwargs can overwrite values like doc, functype, etc.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def node_func(self):
        """Return node function, the node function cannot be reset."""
        return self._node_func

    @property
    def __signature__(self):
        """Node signature for inspection."""
        return signature(self.node_func)

    @property
    def signature(self):
        """Return signature."""
        return self.__signature__

    def convert_func(self, func, inputs):
        """Convert function to a node function.

        For ``numpy.ufunc`` and builtin type, the "inputs" argument is required.

        If inputs are provided, the signature is
        changed based on the inputs and keyword-only.
        If the "inputs" is None, the signature is changed keyword only,
        and the default values are removed.

        The keyword-only design reduced binding overhead during the function
        calls, and allow more consistency between node, modifier, and model.
        """

        if isinstance(func, Model):
            func = func.model_func

        if not has_signature(func) or isinstance(func, np.ufunc):
            if not inputs:
                raise Exception(f"'inputs' required for node {repr(self.name)}")
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

        # if the the function is updated, the inputs are reset
        if "func" in kwargs:
            kwargs["inputs"] = kwargs.get("inputs", None)
        con_dict.update(kwargs)

        return self.__class__(**con_dict)

    def __call__(self, *args, **kwargs):
        """Node function callable.

        The ``node_func`` method is used internally. The ``__call__`` method
        is used for external calls.
        """

        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()  # There's no defaults allowed, added regardless
        return self.node_func(**bound.arguments)

    def __str__(self):
        return nodeformatter(self)
