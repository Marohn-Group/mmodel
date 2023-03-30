"""Test metadata module."""

import pytest
import mmodel.metadata as meta
from types import SimpleNamespace
from textwrap import dedent


class TestMetaDataFormatter:
    """Test MetaDataFormatter class."""

    def test_metaorder_empty(self):
        """Test constructor if the order is empty list.

        If the order is empty list, the formatter should return an empty list.
        However, if the order is None (not defined), the formatter should return
        based on the dictionary keys order.
        """

        formatter = meta.MetaDataFormatter({})
        assert formatter({"a": 1}) == ["a: 1"]

        formatter = meta.MetaDataFormatter({}, [])
        assert formatter({"a": 1}) == []

    def test_None_key(self):
        """Test default formatting."""

        formatter = meta.MetaDataFormatter({}, [None])
        assert formatter({"a": 1}) == [""]

    def test_key_not_in_metadata(self):
        """Test key not in metadata."""

        formatter = meta.MetaDataFormatter({}, ["a"])
        assert formatter({"b": 1}) == []

    def test_formatter_order_defined(self):
        """Test the order of formatter if metaorder is defined."""

        formatter = meta.MetaDataFormatter({}, ["a", "b"])
        assert formatter({"b": "str", "a": 1}) == ["a: 1", "b: str"]

    def test_formatter_order_undefined(self):
        """Test the order of formatter if metaorder is not defined.

        The order should default to the dictionary keys order.
        """

        formatter = meta.MetaDataFormatter({}, None)
        assert formatter({"b": "str", "a": 1}) == ["b: str", "a: 1"]

    def test_formatter(self):
        """Test formatter with formatter functions defined."""

        def formatter(key, value):
            return [f"{key}: {repr(value)}"]

        formatter = meta.MetaDataFormatter({"a": formatter}, ["a"])
        assert formatter({"a": "str"}) == ["a: 'str'"]


def test_format_func():
    """Test format_func function."""

    assert meta.format_func("a", lambda x: x) == ["<lambda>(x)"]


def test_format_listargs():
    """Test format_listargs function."""

    assert meta.format_listargs("a", []) == []
    assert meta.format_listargs(
        "a", [(lambda x: x, {"x": 1}), (lambda y: y, {"x": "str"})]
    ) == ["a:", "\t- <lambda>(1)", "\t- <lambda>('str')"]


def test_format_args():
    """Test format_args function."""

    assert meta.format_args("a", None) == []
    assert meta.format_args("a", (lambda x: x, {"x": 1})) == ["a: <lambda>(1)"]


def test_foramt_returns():
    """Test format_returns function."""

    assert meta.format_returns("a", []) == ["a: None"]
    assert meta.format_returns("a", ["c"]) == ["a: c"]
    assert meta.format_returns("a", ["d", "e"]) == ["a: (d, e)"]


def test_format_value():
    """Test format_value function."""

    assert meta.format_value("a", "str") == ["str"]


def test_format_obj():
    """Test format_obj function."""

    obj = SimpleNamespace(name="object")
    assert meta.format_obj("a", obj) == ["a: object"]


def test_format_obj_func():
    """Test format_obj on function."""

    def func():
        pass

    assert meta.format_obj("a", func) == ["a: func"]

def test_format_obj_without_name():
    """Test format_obj on an object without name attribute."""

    assert meta.format_obj("a", "func") == []


def test_textwrapper():
    """Test textwrapper function."""

    test_str = "This is a test string. With long lines, \ttab, and\nwhitespaces."

    wrapped_str = """\
    This is a test
      string. With long
      lines,   tab, and
      whitespaces."""

    wrapper = meta.textwrapper(width=20, indent=2)
    wrapped = "\n".join(wrapper.wrap(test_str))
    assert wrapped == dedent(wrapped_str)


class TestFormatMetadata:
    """Test format_metadata function."""

    @pytest.fixture
    def metadata(self):
        """Return metadata dictionary."""

        return {
            "a": 1,
            "b": "str",
            "c": lambda x: x,
            "d": [(lambda x: x, {"x": 1}), (lambda y: y, {"x": "str"})],
            "e": (lambda x: x, {"x": 1}),
            "f": ["c"],
            "g": ["d", "e"],
            "h": SimpleNamespace(name="object"),
            "k": "This is a long test string for test character wrapping.",
        }

    @pytest.fixture
    def formatter(self):
        """Return formatter instance"""

        return meta.MetaDataFormatter(
            {
                "c": meta.format_func,
                "d": meta.format_listargs,
                "e": meta.format_args,
                "f": meta.format_returns,
                "g": meta.format_returns,
                "h": meta.format_obj,
                "k": meta.format_value,
            },
            ["a", "b", "c", None, "d", "e", "f", "g", "h", None, "k"],
        )

    @pytest.fixture
    def wrapper(self):
        """Return textwrapper instance."""

        return meta.textwrapper(width=40, indent=2)

    def test_format_metadata(self, metadata, formatter, wrapper):
        """Test the complete."""

        expected = """\
        a: 1
        b: str
        <lambda>(x)

        d:
          - <lambda>(1)
          - <lambda>('str')
        e: <lambda>(1)
        f: c
        g: (d, e)
        h: object
        
        This is a long test string for test
          character wrapping."""

        formatted_metadata = meta.format_metadata(metadata, formatter, wrapper)
        assert "\n".join(formatted_metadata) == dedent(expected)

    def test_format_metadata_no_wrapper(self, metadata, formatter):
        """Test format_metadata without textwrapper."""

        expected = """\
        a: 1
        b: str
        <lambda>(x)

        d:
        \t- <lambda>(1)
        \t- <lambda>('str')
        e: <lambda>(1)
        f: c
        g: (d, e)
        h: object

        This is a long test string for test character wrapping."""

        formatted_metadata = meta.format_metadata(metadata, formatter, None)
        assert "\n".join(formatted_metadata) == dedent(expected)
