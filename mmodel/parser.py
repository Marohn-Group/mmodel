import types
from mmodel.modifier import redefine_signature, redefine_pos_signature
import numpy as np
from mmodel.model import Model
import inspect
import re


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

    def __call__(self, node, func, output, inputs, modifiers, **kwargs):
        """Check if the function belongs to the correct type.

        Returns customized dictionary if that is true. It is possible
        that some of the function options overlap when the list goes
        long, the order of the parser is important.
        """

        if "doc" in kwargs:
            doc = kwargs["doc"]
        else:
            doc = ""
        for parser in self._parser_dict.values():
            attr_dict = parser(
                node=node,
                func=func,
                output=output,
                inputs=inputs,
                modifiers=modifiers,
                **kwargs,
            )
            if attr_dict:
                func = attr_dict["_func"]
                # apply the modifiers
                for mdf in modifiers:
                    func = mdf(func)

                sig = inspect.signature(func)

                base_dict = {
                    "func": func,
                    "sig": sig,
                    "output": output,
                    "modifiers": modifiers,
                    "doc": doc,
                }
                # attr dict can overwrite the base dict
                base_dict.update(attr_dict)
                return base_dict


def grab_docstring(docstring):
    """Parse docstring from built-in function and numpy.ufunc.

    The built-in and ufunc type docstring location is not consistent
    some module/function has the repr at the first line, and some don't.
    Here we try to grab the first line that starts with an upper case
    and ends with a period.
    """

    doc = ""
    for line in docstring.splitlines():
        line = line.strip()
        if line and line[0].isupper() and line.endswith("."):
            doc = line
            break
    return doc


def parse_default(node, func, inputs, **kwargs):
    """Return the default function dictionary.

    The function needs to have the start uppercase and end period style of
    docstring.
    """

    if callable(func):
        func_dict = {}

        doc = ""
        if hasattr(func, "__doc__") and func.__doc__:
            doc = grab_docstring(func.__doc__)

        func_dict["doc"] = doc

        if inputs:
            func = redefine_signature(inputs)(func)

        func_dict.update({"_func": func, "functype": "callable"})
        return func_dict

    else:
        raise Exception(f"Node {repr(node)} has invalid function type.")


def parse_builtin(node, func, inputs, **kwargs):
    """Check if the function is a built-in function."""
    if isinstance(func, types.BuiltinFunctionType):

        doc = grab_docstring(func.__doc__)

        if inputs:
            func = redefine_pos_signature(inputs)(func)
        else:
            raise Exception(
                f"Node {repr(node)} built-in type function "
                "requires 'inputs' definition."
            )

        return {"_func": func, "functype": "builtin", "doc": doc}


def parse_ufunc(node, func, inputs, **kwargs):
    """Check if the function is a numpy universal function.

    The documentation of the universal function is normally the third line.
    """
    if isinstance(func, np.ufunc):

        doc = grab_docstring(func.__doc__)

        if inputs:
            func = redefine_pos_signature(inputs)(func)
        else:
            raise Exception(
                f"Node {repr(node)} numpy.ufunc type function "
                "requires 'inputs' definition."
            )

        return {"_func": func, "functype": "numpy.ufunc", "doc": doc}


def parse_lambda(node, func, output, inputs, **kwargs):
    """Check if the function is a lambda function.

    There is no good way to directly extract the lambda function.
    The inspect.getsource() function extracts the whole source code,
    the lambda function is parsed with regex expression. However,
    this is not a robust solution, recommend to define the doc attribute
    directly.
    """
    if hasattr(func, "__code__") and func.__code__.co_name == "<lambda>":

        pattern_prefix = (
            r"[\'|\"]{}[\'|\"]\s*,\s*"
            r"lambda\s[a-zA-Z,_ ]*:\s*(.*)"
            r",\s*[\'|\"]{}[\'|\"]\s*".format(node, output)
        )
        pattern = r"lambda\s[a-zA-Z,_ ]*:\s*(.*),"
        try:
            full_expression = inspect.getsource(func)
            if full_expression.strip().startswith("lambda"):
                matched = re.search(pattern, full_expression)
            else:
                matched = re.search(pattern_prefix, full_expression)
            if matched:
                doc = f"Lambda expression: {matched.group(1)}."
            else:
                doc = ""
        except OSError:  # could not get source code
            doc = ""
        if inputs:
            raise Exception(
                f"Node {repr(node)} lambda type function "
                "does not support 'inputs' definition."
            )

        return {"_func": func, "functype": "lambda", "doc": doc}


def parse_model(func, inputs, **kwargs):
    """Check if the function is a Model class instance."""

    if isinstance(func, Model):

        doc = ""
        if func.description.splitlines():
            doc = func.description.splitlines()[0]

        if inputs:
            func = redefine_signature(inputs)(func)

        return {"_func": func, "functype": "mmodel.Model", "doc": doc}


node_parser = NodeParser(
    {
        "buitin": parse_builtin,
        "numpy.ufunc": parse_ufunc,
        "mmodel.Model": parse_model,
        "lambda": parse_lambda,
        "default": parse_default,
    }
)
