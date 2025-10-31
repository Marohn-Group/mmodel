"""Test metadata module."""

import pytest
import mmodel.metadata as meta
from types import SimpleNamespace as SNs
from textwrap import dedent, TextWrapper
import functools
from dataclasses import FrozenInstanceError
import numpy as np
import operator


@pytest.fixture
def wrap():
    """Return a wrapper function."""

    return TextWrapper(
        width=20,
        replace_whitespace=False,
        expand_tabs=True,
        tabsize=3,
    )


class TestMetaDataFormatter:
    """Test MetaDataFormatter class."""

    def test_metaorder_empty(self, wrap):
        """Test constructor if the order is an empty list.

        If the order is an empty list, the formatter should return an empty list.
        However, if the order is None (not defined), the formatter should return
        based on the dictionary keys order.
        """

        formatter = meta.MetaDataFormatter({}, [], wrap)
        assert formatter(SNs(a=1)) == ""

    def test_None_key(self, wrap):
        """Test default formatting."""

        formatter = meta.MetaDataFormatter({}, ["_"], wrap)
        assert formatter(SNs(a=1)) == ""

    def test_key_not_in_metadata(self, wrap):
        """Test key not in metadata."""

        formatter = meta.MetaDataFormatter({}, ["a"], wrap)
        assert formatter(SNs(b=1)) == ""

    def test_formatter_order_defined(self, wrap):
        """Test the order of formatter if metaorder is defined."""

        formatter = meta.MetaDataFormatter({}, ["a", "b"], wrap)
        assert formatter(SNs(a=1, b="str")) == "a: 1\nb: str"

    def test_formatter(self, wrap):
        """Test formatter with formatter functions defined."""

        def repr_formatter(key, value):
            return [f"{key}: {repr(value)}"]

        formatter = meta.MetaDataFormatter({"a": repr_formatter}, ["a"], wrap)
        assert formatter(SNs(a="str")) == "a: 'str'"

    def test_forzen_dataclass(self, wrap):
        """Test formatter object is frozen."""

        formatter = meta.MetaDataFormatter({}, ["a"], wrap)
        with pytest.raises(FrozenInstanceError, match="cannot assign to field 'a'"):
            formatter.a = 1

    def test_wrapping(self, wrap):
        """Test wrapping text."""

        wrapped_str = """\
        a: This is a test
        string. With long
        lines,   tab, and
        whitespaces."""

        formatter = meta.MetaDataFormatter({}, ["a"], wrap)
        assert formatter(
            SNs(a="This is a test string. With long lines, \ttab, and\nwhitespaces.")
        ) == dedent(wrapped_str)

    def test_shorten(self, wrap):
        """Test shorten options."""

        formatter = meta.MetaDataFormatter({}, ["a"], wrap, ["a"], shorten_placeholder=" [...]")
        assert (
            formatter(SNs(a="This is a test string for testing shorten options."))
            == "a: This is a [...]"
        )

    def test_shorten_multiline(self, wrap):
        """Test shorten options."""

        shorten_str = """\
        a:
        - This is a test ...
        - a short string
        - Again a very ..."""

        formatter = meta.MetaDataFormatter({"a": meta.format_list}, ["a"], wrap, ["a"])
        assert formatter(
            SNs(
                a=[
                    "This is a test string for testing shorten options.",
                    "a short string",
                    "Again a very long sentence.",
                ]
            )
        ) == dedent(shorten_str)


class TestFormatFunction:
    """Test all format functions."""

    def test_format_func(self):
        """Test format_func function."""

        assert meta.format_func("a", None) == []
        assert meta.format_func("a", lambda x: x) == ["<lambda>(x)"]

    def test_format_list(self):
        """Test format_list function."""

        assert meta.format_list("a", [1, "str"]) == ["a:", "\t- 1", "\t- str"]

    def test_format_list_empty(self):
        """Test format_list function with empty list."""

        assert meta.format_list("a", []) == []

    def test_format_dictargs(self):
        """Test format_dictargs function."""

        assert meta.format_dictargs("a", {"b": 1, "c": "str"}) == [
            "a:",
            "\t- b: 1",
            "\t- c: str",
        ]

    def test_format_dictargs_empty(self):
        """Test format_dictargs function with empty dictionary."""

        assert meta.format_dictargs("a", {}) == []

    def test_format_shortdocstring(self):
        """Test format_shortdocstring function."""

        def test_func():
            """This is a short docstring.

            This is the extended part of docstring."""
            return

        def test_incorrect_docstring():
            """this is a short docstring without a period
            this is a short docstring without capital letter."""
            return

        assert meta.format_shortdocstring("test", test_func.__doc__) == [
            "This is a short docstring."
        ]

        # incorrect docstring
        assert meta.format_shortdocstring("test", test_incorrect_docstring.__doc__) == [
            "this is a short docstring without a period"
        ]

        # built-in
        assert meta.format_shortdocstring("test", operator.add.__doc__) == [
            "Same as a + b."
        ]
        # numpy ufunc
        assert meta.format_shortdocstring("test", np.add.__doc__) == [
            "Add arguments element-wise."
        ]

        # numpy regular function
        assert meta.format_shortdocstring("test", np.sum.__doc__) == [
            "Sum of array elements over a given axis."
        ]

        # lambda
        assert meta.format_shortdocstring("test", (lambda x: x).__doc__) == []

    def test_foramt_returns(self):
        """Test format_returns function."""

        assert meta.format_returns("a", []) == ["a: None"]
        assert meta.format_returns("a", ["c"]) == ["a: c"]
        assert meta.format_returns("a", ["d", "e"]) == ["a: (d, e)"]

    def test_format_value(self):
        """Test format_value function."""

        assert meta.format_value("a", None) == []
        assert meta.format_value("a", "str") == ["str"]

    def test_format_obj_name(self):
        """Test format_obj_name function."""

        obj = SNs(name="object")
        assert meta.format_obj_name("a", obj) == ["a: object"]
        assert meta.format_obj_name("a", None) == []

    def test_format_obj_name_func(self):
        """Test format_obj_name on function."""

        def func():
            pass

        assert meta.format_obj_name("a", func) == ["a: func"]

    def test_format_obj_name_without_name(self):
        """Test format_obj_name on an object without name attribute."""

        assert meta.format_obj_name("a", SNs(a=1)) == ["a: namespace(a=1)"]

    def test_format_dictkeys(self):
        """Test format_dictkeys function."""

        assert meta.format_dictkeys("a", {"b": 1, "c": "str"}) == ["a: ['b', 'c']"]


class TestModifierMetadata:
    """Test modifier metadata functions."""

    @pytest.fixture
    def modifier_with_meta(self):
        """Closure with arguments and "metadata" attribute."""

        def mod(value):
            def wrapper(func):
                @functools.wraps(func)
                def wrapped(*args, **kwargs):
                    return func(*args, **kwargs) + value

                return wrapped

            wrapper.metadata = f"modifier({value})"
            return wrapper

        return mod

    @pytest.fixture
    def modifier(self):
        """Closure without arguments."""

        def modifier(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapped

        return modifier

    def test_modifier_metadata(self, value_modifier, modifier_with_meta, modifier):
        """Test modifier_metadata function."""

        assert meta.modifier_metadata(value_modifier(1)) == "add_value(value=1)"
        assert meta.modifier_metadata(modifier_with_meta(1)) == "modifier(1)"
        assert meta.modifier_metadata(modifier) == "modifier"

    def test_format_modifierlist(self, value_modifier, modifier_with_meta, modifier):
        """Test format_modifierlist function."""

        assert meta.format_modifierlist(
            "modifier", [value_modifier(1), modifier_with_meta(1), modifier]
        ) == [
            "modifier:",
            "\t- add_value(value=1)",
            "\t- modifier(1)",
            "\t- modifier",
        ]


class TestFormatedString:
    """Test final formatted string."""

    @pytest.fixture
    def metadata_obj(self):
        """Return the a namespace object."""

        return SNs(
            a=1,
            b="str",
            c=lambda x: x,
            d=["element1", 2],
            e={},
            f="c",
            g=["d", "e"],
            h=SNs(name="object"),
            i=SNs(noname="none"),
            j=operator.add.__doc__,
            k="This is a long test string for test character wrapping.",
            m="This is a long test string for test character shortening.",
            o="repr representation",
        )

    @pytest.fixture
    def formatter(self):
        """Return formatter instance."""

        return meta.MetaDataFormatter(
            {
                "c": meta.format_func,
                "d": meta.format_list,
                "f": meta.format_returns,
                "g": meta.format_returns,
                "h": meta.format_obj_name,
                "i": meta.format_obj_name,
                "j": meta.format_shortdocstring,
                "k": meta.format_value,
                "m": meta.format_value,
                "o": lambda key, value: [f"p: {repr(value)}"],
                "empty": lambda k, v: [f"{k}: {v}"],
                "last": meta.format_shortdocstring,  # empty string
            },
            [
                "a",
                "b",
                "c",
                "_",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "_",
                "k",
                "o",
                "empty",
                "m",
                "last",
            ],
            TextWrapper(
                width=40,
                subsequent_indent="  ",
                replace_whitespace=False,
                expand_tabs=True,
                tabsize=2,
            ),
            ["j", "m"],
        )

    def test_format_metadata(self, metadata_obj, formatter):
        """Test the complete metadata representation.

        The end string needs to be stripped if the last line is an empty string.
        """

        expected = """\
        a: 1
        b: str
        <lambda>(x)

        d:
          - element1
          - 2
        f: c
        g: (d, e)
        h: object
        i: namespace(noname='none')
        Same as a + b.

        This is a long test string for test
          character wrapping.
        p: 'repr representation'
        empty: None
        This is a long test string for test ..."""

        assert formatter(metadata_obj) == dedent(expected)
