import types
from mmodel.modifier import signature_modifier, pos_signature_modifier
import numpy as np
from mmodel.model import Model
import inspect


class NodeParser:
    """Output node attribute based on inputs.

    The class check function outputs the necessary properties
    of the function and add it to the node attribute.

    The class currently supports Python built-in functions, regular
    function, numpy.ufunc, and Model class instance.

    To add additional function types, subclass this class.
    """

    def __init__(self, parser_dict):
        self._parser_dict = parser_dict

    def __call__(self, node, func, output, inputs, modifiers):
        """Check if the function belongs to the correct type.

        Returns customized dictionary if that is true. It is possible
        that some of the function options overlap when the list goes
        long, the order of the parser is important.
        """
        for parser in self._parser_dict.values():
            attr_dict = parser(node, func, output, inputs, modifiers)
            if attr_dict:
                func = attr_dict["_func"]
                # apply the modifiers
                for mdf, kwargs in modifiers:
                    func = mdf(func, **kwargs)

                sig = inspect.signature(func)
                base_dict = {
                    "func": func,
                    "sig": sig,
                    "output": output,
                    "modifiers": modifiers,
                }
                # attr dict can overwrite the base dict
                attr_dict.update(base_dict)
                return attr_dict


def default_parser(node, func, output, inputs, modifiers):
    """Return the default function dictionary."""
    if callable(func):
        func_dict = {}

        if hasattr(func, "__doc__"):
            func_dict["doc"] = func.__doc__

        if inputs:
            func = signature_modifier(func, inputs)

        func_dict.update({"_func": func, "functype": "callable"})
        return func_dict

    else:
        raise Exception(f"Node {repr(node)} has invalid function type.")


def builtin_parser(node, func, output, inputs, modifiers):
    """Check if the function is a built-in function.

    The built-in type docstring location is not consistent
    some module/function has the repr at the first line, and some don't.
    Here we try to grab the first line that starts with an upper case
    and ends with a period.
    """
    if isinstance(func, types.BuiltinFunctionType):

        doc = ""
        for line in func.__doc__.splitlines():
            if line and line[0].isupper() and line.endswith("."):
                doc = line
                break

        if inputs:
            func = pos_signature_modifier(func, inputs)
        else:
            raise Exception(
                f"Node {repr(node)} built-in type function "
                "requires 'inputs' definition."
            )

        return {"_func": func, "functype": "builtin", "doc": doc}


def ufunc_parser(node, func, output, inputs, modifiers):
    """Check if the function is a numpy universal function.

    The documentation of the universal function is normally the third line.
    """
    if isinstance(func, np.ufunc):

        doc = func.__doc__.splitlines()[2]

        if inputs:
            func = pos_signature_modifier(func, inputs)
        else:
            raise Exception(
                f"Node {repr(node)} numpy.ufunc type function "
                "requires 'inputs' definition."
            )

        return {"_func": func, "functype": "numpy.ufunc", "doc": doc}


def model_parser(node, func, output, inputs, modifiers):
    """Check if the function is a Model class instance."""

    if isinstance(func, Model):

        doc = func.description.splitlines()[0]

        if inputs:
            func = signature_modifier(func, inputs)

        return {"_func": func, "functype": "mmodel.Model", "doc": doc}


parser_engine = NodeParser(
    {
        "buitin": builtin_parser,
        "numpy.ufunc": ufunc_parser,
        "mmodel.Model": model_parser,
        "default": default_parser,
    }
)