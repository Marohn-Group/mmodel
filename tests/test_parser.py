from mmodel.parser import (
    node_parser,
    parse_default,
    parse_ufunc,
    parse_model,
    parse_builtin,
    grab_docstring,
    parse_lambda,
)
from mmodel.model import Model
from mmodel.handler import BasicHandler
import pytest
import math
import inspect
import numpy as np
import operator


def test_parse_docstring():
    """Test grab_docstring against some of the built-in and numpy.ufunc."""

    assert grab_docstring(np.sum.__doc__) == "Sum of array elements over a given axis."
    assert grab_docstring(np.add.__doc__) == "Add arguments element-wise."
    assert (
        grab_docstring(math.log.__doc__)
        == "Return the logarithm of x to the given base."
    )
    assert (
        grab_docstring(math.acos.__doc__)
        == "Return the arc cosine (measured in radians) of x."
    )
    assert (
        grab_docstring(print.__doc__)
        == "Prints the values to a stream, or to sys.stdout by default."
    )
    assert grab_docstring(operator.add.__doc__) == "Same as a + b."


class TestDefaultParser:
    @pytest.fixture
    def callable_func(self):
        """Construct a callable function."""

        def func(a, b):
            """Sum of a and b.

            The detailed docstring.
            """
            return a + b

        return func

    def test_default_parser(self, callable_func):
        """Test default parser correctly parse callable."""

        assert parse_default("test", callable_func, []) == {
            "_func": callable_func,
            "doc": "Sum of a and b.",
            "functype": "callable",
        }

    def test_default_parser_without_doc(self):
        """Test default parser correctly parse function without doc."""

        func = lambda x: x
        assert parse_default("test", func, []) == {
            "_func": func,
            "doc": "",
            "functype": "callable",
        }

    def test_default_parser_input(self, callable_func):
        """Test default parser change inputs."""

        func = parse_default("test", callable_func, ["x", "y"])["_func"]
        assert list(inspect.signature(func).parameters) == ["x", "y"]

    def test_default_parser_raises(self):
        """Test if the function is not a callable an exception is raised."""

        with pytest.raises(Exception, match="Node 'test' has invalid function type."):
            # use an integer
            parse_default("test", 1, ["x", "y"])


class TestBuiltinParser:
    def test_builtin_parser(self):
        """Test default parser correctly parse built-in function."""

        func_dict = parse_builtin("test", math.pow, ["a", "b"])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Return x**y (x to the power of y).",
            "functype": "builtin",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b"]

    def test_builtin_parser_long_doc(self):
        """Test parse_builtin correctly parse built-in function."""

        func_dict = parse_builtin("test", print, ["a"])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Prints the values to a stream, or to sys.stdout by default.",
            "functype": "builtin",
        }
        assert list(inspect.signature(func).parameters) == ["a"]

    def test_builtin_parser_raises(self):
        """Test if an exception is raised when the inputs parameters are not defined."""

        with pytest.raises(
            Exception,
            match="Node 'test' built-in type function requires 'inputs' definition.",
        ):
            # use an integer
            parse_builtin("test", print, [])


class TestufuncParser:
    """Test numpy parse_ufunc."""

    def test_ufunc_parser(self):
        """Test ufunc parser correctly parse numpy.ufunc."""

        func_dict = parse_ufunc("test", np.add, ["a", "b"])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Add arguments element-wise.",
            "functype": "numpy.ufunc",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b"]

    def test_ufunc_parser_raises(self):
        """Test exception is raised when inputs parameters are not defined."""

        with pytest.raises(
            Exception,
            match="Node 'test' numpy.ufunc type function requires 'inputs' definition.",
        ):
            # use an integer
            parse_ufunc("test", np.add, [])


class TestLambdaParser:
    """Test lambda parser."""

    def test_lambda_parser(self):
        """Test lambda parser correctly parse lambda function."""

        func_dict = parse_lambda("test", lambda x, y: x + y, "c", [])
        assert func_dict["doc"] == "Lambda expression: x + y."
        assert func_dict["functype"] == "lambda"

    def test_lambda_parser_complex(self):
        """Test lambda parser with complex lambda function and with its own line."""

        func_dict = parse_lambda(
            "test", lambda x, y: [x**2 for x in y if x in {"x": 1} or x > 2], "c", []
        )
        assert (
            func_dict["doc"]
            == 'Lambda expression: [x**2 for x in y if x in {"x": 1} or x > 2].'
        )

    def test_lambda_parser_raises(self):
        """Test exception is raised when inputs parameters are not defined."""

        with pytest.raises(
            Exception,
            match="Node 'test' lambda type function does not support 'inputs' definition.",
        ):
            # use an integer
            parse_lambda("test", lambda x, y: (x, y), "c", ["a", "b"])


class TestModelParser:
    """Test mmodel Model instance parser."""

    @pytest.fixture
    def func(self, mmodel_G):
        """Construct a model_instance."""
        description = "The first line of description.\nThe second line of description."
        return Model("model_instance", mmodel_G, BasicHandler, description=description)

    def test_model_parser(self, func):
        """Test ufunc parser correctly parse model instances."""

        func_dict = parse_model(func, [])
        assert func_dict == {
            "_func": func,
            "doc": "The first line of description.",
            "functype": "mmodel.Model",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b", "d", "f"]

    def test_model_parser_inputs(self, func):
        """Test ufunc parser correctly parse model instances with inputs."""

        func_dict = parse_model(func, ["x", "y", "z", "xy"])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "The first line of description.",
            "functype": "mmodel.Model",
        }
        assert list(inspect.signature(func).parameters) == ["x", "y", "z", "xy"]


class TestNodeParser:
    @pytest.fixture
    def model_func(self, mmodel_G):
        """Construct a model_instance."""
        description = "The first line of description.\nThe second line of description."
        return Model("model_instance", mmodel_G, BasicHandler, description=description)

    @pytest.fixture
    def callable_func(self):
        """Construct a callable function."""

        def func(a, b):
            """Sum of a and b."""
            return a + b

        return func

    def test_parse_builtin(self, value_modifier):
        """Test the full node attributes for builtin function."""
        mod = value_modifier(value=2)
        func_dict = node_parser("test", math.pow, "c", ["a", "b"], [mod])
        func_dict.pop("_func")

        sig = func_dict.pop("sig")

        assert list(sig.parameters) == ["a", "b"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Return x**y (x to the power of y).",
            "functype": "builtin",
            "modifiers": [mod],
            "output": "c",
        }

        assert func(a=1, b=2) == 3  # 1 + 2 (from modifier)

    def test_parse_ufunc(self, value_modifier):
        """Test the full node attributes for numpy.ufunc."""

        mod = value_modifier(value=1)
        func_dict = node_parser("test", np.add, "c", ["a", "b"], [mod])
        func_dict.pop("_func")

        sig = func_dict.pop("sig")

        assert list(sig.parameters) == ["a", "b"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Add arguments element-wise.",
            "functype": "numpy.ufunc",
            "modifiers": [mod],
            "output": "c",
        }

        assert np.array_equal(func(a=np.array([1, 2, 3]), b=2), np.array([4, 5, 6]))

    def test_parse_model(self, model_func):
        """Test the full node attributes for mmodel.model."""

        func_dict = node_parser("test", model_func, "c", ["x", "y", "z", "xy"], [])
        func_dict.pop("_func")

        sig = func_dict.pop("sig")

        assert list(sig.parameters) == ["x", "y", "z", "xy"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "The first line of description.",
            "functype": "mmodel.Model",
            "modifiers": [],
            "output": "c",
        }

        assert func(x=10, y=2, z=15, xy=1) == (-36, math.log(12, 2))

    def test_parse_callable(self, value_modifier, callable_func):
        """Test the full node attributes for callable."""

        mod = value_modifier(value=-1)
        func_dict = node_parser("test", callable_func, "c", ["x", "y"], [mod])
        func_dict.pop("_func")
        sig = func_dict.pop("sig")
        assert list(sig.parameters) == ["x", "y"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Sum of a and b.",
            "functype": "callable",
            "modifiers": [mod],
            "output": "c",
        }

        assert func(x=10, y=2) == 11

    def test_parse_lambda(self, value_modifier, callable_func):
        """Test the full node attributes for callable."""

        mod = value_modifier(value=-1)
        func_dict = node_parser("test", lambda x, y: x + y, "c", [], [mod])
        func_dict.pop("_func")
        sig = func_dict.pop("sig")
        assert list(sig.parameters) == ["x", "y"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Lambda expression: x + y.",
            "functype": "lambda",
            "modifiers": [mod],
            "output": "c",
        }

        assert func(x=10, y=2) == 11
