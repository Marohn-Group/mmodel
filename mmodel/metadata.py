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

        self.frommatter = formatter
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
            if key in self.frommatter:
                metadata_str_list.extend(self.frommatter[key](key, metadata[key]))
            else:
                metadata_str_list.extend([f"{key}: {metadata[key]}"])

        return metadata_str_list


def format_func(key, value):
    """Format the metadata value that has a function.

    The key name is not shown in the string output.
    The result is func(args1, args2, ...)"""

    return [f"{value.__name__}{inspect.signature(value)}"]


def format_listargs(key, value):
    """Format the metadata value that has a list of (func, kwargs).

    The formatter is for modifiers and other metadata that have a
    list of (func, kwargs), and kwargs is a dictionary.
    """

    if value:
        str_list = [f"{key}:"]

        for func, kwargs in value:
            str_value = [repr(v) for v in kwargs.values()]
            mod_str = f"\t- {func.__name__}({', '.join(str_value)})"
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
    """Format the metadata without displaying key."""
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
        "handler": format_args,
        "modifiers": format_listargs,
        "description": format_value,
    },
    ["model", "returns", "graph", "handler", "modifiers", None, "description"],
)

nodeformatter = MetaDataFormatter(
    {
        "node": format_value,
        "func": format_func,
        "modifiers": format_listargs,
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
