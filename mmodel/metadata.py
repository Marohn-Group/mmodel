import inspect
from textwrap import TextWrapper, shorten
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetaDataFormatter:
    """Metadata Formatter."""

    formatter_dict: dict
    meta_order: list
    text_wrapper: callable
    shorten_list: list = field(default_factory=list)
    shorten_placeholder: str = " ..."

    def __call__(self, obj):
        """Convert metadata dictionary to string.

        The process returns a list of metadata by lines.
        If the formatter is not found in the formatter dictionary,
        the default string output is "key: value".

        :param dict formatter_dict: format function dictionary
        :param list meta_order: metadata key order, entry is None if linebreak needed.
            Defaults to dictionary key order.
        """

        metadata_list = []
        for key in self.meta_order:
            if key == "_":  # linebreak
                metadata_list.append("")
                continue

            if key == "self":  # allow reference self
                value = obj
            else:
                value = getattr(obj, key, None)

            # the format functions return a list, for potential multi-liners strings
            if key in self.formatter_dict:
                entry = self.formatter_dict[key](key, value)
            elif value:
                entry = [f"{key}: {value}"]
            else:
                entry = []

            if key in self.shorten_list:
                # replace the original list
                entry = [
                    shorten(
                        ele,
                        width=self.text_wrapper.width,
                        placeholder=self.shorten_placeholder,
                    )
                    for ele in entry
                ]

            metadata_list.extend(entry)

        metadata_wrapped = []
        for line in metadata_list:
            if line:
                metadata_wrapped.extend(self.text_wrapper.wrap(line))
            else:
                metadata_wrapped.append("")

        return "\n".join(metadata_wrapped).strip()


def format_func(key, value):
    """Format the metadata value that has a function.

    The key name is not shown in the string output.
    The result is func(args1, args2, ...)."""

    if not value:
        return []

    return [f"{value.__name__}{inspect.signature(value)}"]


def format_list(key, value):
    """Format the metadata value that is a list."""

    if not value:
        return []
    elements = [f"\t- {v}" for v in value]
    return [f"{key}:"] + elements


def format_dictargs(key, value):
    """Format the metadata value that is a dictionary."""

    if not value:
        # return [f"{key}: []"]
        return []

    elements = [f"\t- {k}: {v}" for k, v in value.items()]
    return [f"{key}:"] + elements


def modifier_metadata(func):
    """Extract metadata from closure, including the name and the arguments.

    The order of extraction:
    1. If the object has the "metadata" attribute defined.
    2. If not, the metadata returns the function name itself.
    """

    if hasattr(func, "metadata"):
        return func.metadata
    else:
        return func.__name__


def format_modifierlist(key, value):
    """Format the metadata that is a list of modifiers.

    The metadata of the modifier is extracted by the modifier_metadata function.
    The resulting list is formatted by the format_list function.
    """

    modifier_str_list = [modifier_metadata(modifier) for modifier in value]

    return format_list(key, modifier_str_list)


def format_shortdocstring(key, value):
    """Format function docstring.

    Only the short docstring is parsed. The built-in and
    ufunc type docstring location is not consistent
    some module/function has the repr at the first line,
    and some don't.
    Here we try to grab the first line that starts with
    an upper case and ends with a period. If the docstring
    is improperly formatted, the first line is used.
    """
    if not value:
        return []

    for line in value.splitlines():
        line = line.strip()
        if line and line[0].isupper() and line.endswith("."):
            doc = line
            return [f"{doc}"]

    return value.splitlines()[:1]


def format_returns(key, value):
    """Format the metadata value that has a list of returns.

    The formatter is for the returns metadata. If the "returns" value is empty,
    the output is None. If the returns only have one value, return the value; otherwise
    , return the values separated by commas in a tuple representation.
    """

    return_len = len(value)

    if not return_len:
        returns_str = "None"
    elif return_len == 1:
        returns_str = value[0]
    else:
        returns_str = f"({', '.join(value)})"

    return [f"{key}: {returns_str}"]


def format_value(key, value):
    """Format the metadata without displaying the key."""

    if not value:
        return []

    return [f"{value}"]


def format_obj_name(key, value):
    """Format the metadata value that is an object.

    Only show the name of the object. This is used for
    graph and handler objects.
    The object needs to have __name__ or name attribute defined.
    If neither is defined, display the string representation.
    """

    if not value:
        return []

    name = getattr(value, "__name__", getattr(value, "name", str(value)))
    return [f"{key}: {name}"]


def format_dictkeys(key, value):
    """Formating function that only shows dictionary keys.

    If the value dictionary is empty return None.
    """

    if value:
        return [f"{key}: {list(value.keys())}"]
    else:
        return [f"{key}: None"]


# customized textwrapper
wrapper80 = TextWrapper(
    width=80,
    subsequent_indent="",
    replace_whitespace=False,
    expand_tabs=True,
    tabsize=0,
)


modelformatter = MetaDataFormatter(
    {
        "self": format_func,
        "returns": format_returns,
        "graph": format_obj_name,
        "handler": format_obj_name,
        "handler_kwargs": format_dictargs,
        "modifiers": format_modifierlist,
        "doc": format_value,
    },
    [
        "self",
        "returns",
        "group",
        "graph",
        "handler",
        "handler_kwargs",
        "modifiers",
        "_",
        "doc",
    ],
    wrapper80,
    ["handler_kwargs", "modifiers"],
)

nodeformatter = MetaDataFormatter(
    {
        "name": format_value,
        "node_func": format_func,
        "output": lambda key, value: [f"return: {value}"],
        "modifiers": format_modifierlist,
        "doc": format_shortdocstring,
    },
    ["name", "_", "node_func", "output", "functype", "modifiers", "_", "doc"],
    wrapper80,
)


def format_group_content(key, value, formatter=modelformatter):
    """Format the metadata value that is a dictionary of model arguments.

    Here use the model formatter dictionary to parse the content.
    """

    if not value:
        return []

    meta_list = [key + ": {"]
    for sub_key, sub_value in value.items():
        if sub_key in formatter.formatter_dict:
            meta_list.extend(formatter.formatter_dict[sub_key](sub_key, sub_value))
        else:
            meta_list.append(f"  {sub_key}: {sub_value}")
    meta_list.append("}")
    return meta_list


modelgroupformatter = MetaDataFormatter(
    {
        "name": format_value,
        "models": format_dictkeys,
        "nodes": format_dictkeys,
        "model_defaults": format_group_content,
        "doc": format_value,
    },
    ["name", "models", "nodes", "model_defaults", "_", "doc"],
    wrapper80,
    ["model_defaults", "nodes"],
)
