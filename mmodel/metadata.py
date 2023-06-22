"""Handle node, graph and model metadata.

The two core types of functions are formatter and wrapper. The formatter
takes care of the formatting of the metadata, and the wrapper takes care
of the wrapping of the metadata.
"""

import inspect
from textwrap import TextWrapper


class MetaDataFormatter:
    """Metadata Formatter."""

    def __init__(self, formatter: dict, metaorder: list = None):
        """Initiate the formatter."""

        self.formatter = formatter
        self.metaorder = metaorder

    def __call__(self, metadata):
        """Convert metadata dictionary to string.

        The process returns a list of metadata by lines.
        If the formatter is not found in the formatter dictionary,
        the default string output is "key: value".

        :param dict metadata: metadata dictionary
        :param list metaorder: metadata key order, entry is None if linebreak needed.
            Defaults to dictionary key order.
        """
        metaorder = self.metaorder if self.metaorder is not None else metadata.keys()
        metadata_str_list = []
        for key in metaorder:
            if key is None:
                metadata_str_list.append("")
                continue
            elif key not in metadata:
                continue
            if key in self.formatter:
                metadata_str_list.extend(self.formatter[key](key, metadata[key]))
            else:
                metadata_str_list.extend([f"{key}: {metadata[key]}"])

        return metadata_str_list


def format_func(key, value):
    """Format the metadata value that has a function.

    The key name is not shown in the string output.
    The result is func(args1, args2, ...)."""

    return [f"{value.__name__}{inspect.signature(value)}"]


def format_list(key, value):
    """Format the metadata value that is a list."""

    if value:
        str_list = [f"{key}:"]
        for v in value:
            str_list.append(f"\t- {v}")
        return str_list
    else:
        return []


def modifier_metadata(closure):
    """Extract metadata from closure, including the name and the arguments.

    The order of extraction:
    1. If the object has the "metadata" attribute defined.
    2. If the closure takes no arguments, the name is the function name.
    3. If the closure takes arguments, the "metadata" attribute is not defined.

    Note::

        inspect.getclosurevars(closure).nonlocals can only parse values
        if the value is used in the closure.
    """

    if hasattr(closure, "metadata"):
        return closure.metadata
    elif not inspect.getclosurevars(closure).nonlocals:
        return closure.__name__

    else:  # closure takes arguments

        # In some rare cases, the closure is a nested function.
        # For example, in the tests, the nested closure reflects the
        # path of the parent function. Here we remove the nested
        # parent function name.

        name = closure.__qualname__.rsplit(".<locals>.")[-2]
        kwargs = inspect.getclosurevars(closure).nonlocals
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        return f"{name}({kwargs_str})"


def format_modifierlist(key, value):
    """Format the metadata that is a list of modifiers.

    The metadata of the modifier is extracted by the modifier_metadata function.
    The resulting list is formatted by the format_list function.
    """

    modifier_str_list = [modifier_metadata(modifier) for modifier in value]

    return format_list(key, modifier_str_list)


def format_dictargs(key, value):
    """Format the metadata value that is a dictionary."""

    if value:
        str_list = [f"{key}:"]

        for k, v in value.items():
            mod_str = f"\t- {k}: {v}"
            str_list.append(mod_str)

        return str_list

    else:
        return []


def format_args(key, value):
    """Format the metadata value that has the value of (func, kwargs).

    The formatter is for the handler metadata.
    """
    if value:
        func, kwargs = value
        return [
            f"{key}: {func.__name__}({', '.join(repr(v) for v in kwargs.values())})"
        ]
    else:
        return []


def format_returns(key, value):
    """Format the metadata value that has a list of returns.

    The formatter is for the returns metadata. If the "returns" value is empty,
    the output is None. If the returns only have 1 value, return the value, else
    return the values separated by commas in a tuple representation.
    """

    return_len = len(value)

    if return_len == 0:
        returns_str = "None"
    elif return_len == 1:
        returns_str = value[0]
    else:
        returns_str = f"({', '.join(value)})"

    return [f"{key}: {returns_str}"]


def format_value(key, value):
    """Format the metadata without displaying the key."""
    if value:
        return [value]
    else:
        return []


def format_obj(key, value):
    """Format the metadata value that is an object.

    Only show the name of the object. This is used for graph objects.
    The object needs to have __name__ or name attribute defined.
    """

    name = getattr(value, "__name__", getattr(value, "name", None))
    if name:
        return [f"{key}: {name}"]
    else:
        return []


modelformatter = MetaDataFormatter(
    {
        "model": format_func,
        "returns": format_returns,
        "graph": format_obj,
        "handler": format_obj,
        "handler args": format_dictargs,
        "modifiers": format_modifierlist,
        "description": format_value,
    },
    [
        "model",
        "returns",
        "graph",
        "handler",
        "handler args",
        "modifiers",
        None,
        "description",
    ],
)

nodeformatter = MetaDataFormatter(
    {
        "node": format_value,
        "func": format_func,
        "modifiers": format_modifierlist,
        "doc": format_value,
    },
    ["node", None, "func", "return", "functype", "modifiers", None, "doc"],
)


def textwrapper(width: int = 80, indent: int = 2):
    """Wrap metadata content.

    The width defaults to 80 characters. The resulting wrapping has no
    initial indentation. The indent parameter is the subsequent indent
    parameter in the wrap function. The tabsize is the same as
    the indent.
    """

    return TextWrapper(
        width=width,
        subsequent_indent=" " * indent,
        replace_whitespace=False,
        expand_tabs=True,
        tabsize=indent,
    )


# Standard textwrapper with 80 characters.
textwrap80 = textwrapper(80, 2)
# shorted textwarpper with 5o characters for nodes.
textwrap50 = textwrapper(50, 2)


def format_metadata(metadata, formatter, textwrapper):
    """Format and wrap the metadata."""

    metadata_list = formatter(metadata)

    if textwrapper:
        metadata_wrapped = []
        for line in metadata_list:
            if line:
                metadata_wrapped.extend(textwrapper.wrap(line))
            else:
                metadata_wrapped.append("")
        return metadata_wrapped

    return metadata_list
