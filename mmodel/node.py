from mmodel.signature import convert_func, get_node_signature, get_parameters
from mmodel.metadata import nodeformatter
from mmodel.utility import construction_dict, modify_func, parse_functype
from inspect import signature


class Node:
    """A node class that formats node function and metadata."""

    def __init__(
        self,
        name,
        func,
        arglist=None,
        kwarglist=None,
        output=None,
        modifiers=None,
        **kwargs,
    ):
        # static
        self.name = self.__name__ = name
        self.output = output

        self._arglist = arglist or []
        self._kwarglist = kwarglist or []
        self._modifiers = modifiers or []

        self.func = func
        self.functype = parse_functype(func)
        self.doc = func.__doc__

        self._base_func = self.convert_func(func, self._arglist, self._kwarglist)
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

    def convert_func(self, func, arglist, kwarglist):
        """Convert function to a node function.

        To replace the positional or positional-or-keyword parameters,
        the list arglist needs to be defined. The user can select
        desired keyword-only parameters with kwarglist. To replace the
        keyword-only parameters, a custom function needs to be defined
        to replace the function.

        For functions that already fit the criteria and have no argument
        list, we still wrap the function. The overhead is minimal.
        """
        param_list = get_parameters(func)
        node_sig = get_node_signature(param_list, arglist, kwarglist)

        return convert_func(func, node_sig)

    @property
    def arglist(self):
        """Return a copy of arglist."""
        return self._arglist.copy()

    @property
    def kwarglist(self):
        """Return a copy of kwarglist."""
        return self._kwarglist.copy()

    @property
    def modifiers(self):
        """Return a copy of modifiers."""
        return self._modifiers.copy()

    def edit(self, **kwargs):
        """Edit node. A new node object is created."""

        con_dict = construction_dict(
            self,
            ["arglist", "kwarglist", "modifiers"],
            ["functype", "doc", "node_func"],
        )

        # if the the function is updated, the inputs are reset
        if "func" in kwargs:
            kwargs["arglist"] = kwargs.get("arglist", None)
            kwargs["kwarglist"] = kwargs.get("kwarglist", None)

        con_dict.update(kwargs)

        return self.__class__(**con_dict)

    def __call__(self, *args, **kwargs):
        """Node function callable.

        The ``node_func`` method is used internally. The ``__call__`` method
        is used for external calls.
        """

        bound = self.signature.bind(*args, **kwargs)
        return self.node_func(**bound.arguments)

    def __str__(self):
        return nodeformatter(self)
