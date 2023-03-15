from mmodel.parser import (
    parser_engine,
    default_parser,
    ufunc_parser,
    model_parser,
    builtin_parser,
)
from mmodel.model import Model
from mmodel.handler import BasicHandler
import pytest
import math
import inspect
import numpy as np
from functools import wraps


class TestDefaultParser:
    @pytest.fixture
    def callable_func(self):
        """Construct a callable function."""

        def func(a, b):
            """Sum of a and b."""
            return a + b

        return func

    def test_default_parser(self, callable_func):
        """Test default parser correctly parse callable."""

        assert default_parser("test", callable_func, "c", [], []) == {
            "_func": callable_func,
            "doc": "Sum of a and b.",
            "functype": "callable",
        }

    def test_default_parser_input(self, callable_func):
        """Test default parser change inputs."""

        func = default_parser("test", callable_func, "c", ["x", "y"], [])["_func"]
        assert list(inspect.signature(func).parameters) == ["x", "y"]

    def test_default_parser_raises(self, callable_func):
        """Test if the function is not a callable an exception is raised."""

        with pytest.raises(Exception, match=f"Node 'test' has invalid function type."):
            # use an integer
            default_parser("test", 1, "c", ["x", "y"], [])["_func"]


class TestBuiltinParser:
    def test_builtin_parser(self):
        """Test default parser correctly parse callable."""

        func_dict = builtin_parser("test", math.pow, "c", ["a", "b"], [])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Return x**y (x to the power of y).",
            "functype": "builtin",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b"]

    def test_builtin_parser_long_doc(self):
        """Test builtin_parser correctly parse callable."""

        func_dict = builtin_parser("test", print, "c", ["a"], [])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Prints the values to a stream, or to sys.stdout by default.",
            "functype": "builtin",
        }
        assert list(inspect.signature(func).parameters) == ["a"]

    def test_builtin_parser_raises(self):
        """Test if the function is not a callable an exception is raised."""

        with pytest.raises(
            Exception,
            match=f"Node 'test' built-in type function requires 'inputs' definition.",
        ):
            # use an integer
            builtin_parser("test", print, "c", [], [])["_func"]


class TestufuncParser:
    """Test numpy ufunc_parser"""

    def test_ufunc_parser(self):
        """Test ufunc parser correctly parse callable."""

        func_dict = ufunc_parser("test", np.add, "c", ["a", "b"], [])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "Add arguments element-wise.",
            "functype": "numpy.ufunc",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b"]

    def test_builtin_parser_raises(self):
        """Test if the function is not a callable an exception is raised."""

        with pytest.raises(
            Exception,
            match=f"Node 'test' numpy.ufunc type function requires 'inputs' definition.",
        ):
            # use an integer
            ufunc_parser("test", np.add, "c", [], [])["_func"]


class TestModelParser:
    """Test mmodel Model instance parser"""

    @pytest.fixture
    def func(self, mmodel_G):
        """Construct a model_instance"""
        description = "The first line of description.\nThe second line of description."
        return Model(
            "model_instance", mmodel_G, (BasicHandler, {}), description=description
        )

    def test_model_parser(self, func):
        """Test ufunc parser correctly parse callable."""

        func_dict = model_parser("test", func, "c", [], [])
        assert func_dict == {
            "_func": func,
            "doc": "The first line of description.",
            "functype": "mmodel.Model",
        }
        assert list(inspect.signature(func).parameters) == ["a", "b", "d", "f"]

    def test_model_parser_inputs(self, func):
        """Test ufunc parser correctly parse callable with inputs."""

        func_dict = model_parser("test", func, "c", ["x", "y", "z", "xy"], [])
        func = func_dict.pop("_func")
        assert func_dict == {
            "doc": "The first line of description.",
            "functype": "mmodel.Model",
        }
        assert list(inspect.signature(func).parameters) == ["x", "y", "z", "xy"]


class TestNodeParser:
    @pytest.fixture
    def modifier(self):
        def modifier_func(func, value):
            """Basic modifier."""

            @wraps(func)
            def wrapper(**kwargs):
                return func(**kwargs) + value

            return wrapper

        return modifier_func

    @pytest.fixture
    def model_func(self, mmodel_G):
        """Construct a model_instance."""
        description = "The first line of description.\nThe second line of description."
        return Model(
            "model_instance", mmodel_G, (BasicHandler, {}), description=description
        )

    @pytest.fixture
    def callable_func(self):
        """Construct a callable function."""

        def func(a, b):
            """Sum of a and b."""
            return a + b

        return func

    def test_parse_builtin(self, modifier):
        """Test the full node attributes for builtin function."""

        func_dict = parser_engine(
            "test", math.pow, "c", ["a", "b"], [(modifier, {"value": 2})]
        )
        func_dict.pop("_func")

        sig = func_dict.pop("sig")

        assert list(sig.parameters) == ["a", "b"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Return x**y (x to the power of y).",
            "functype": "builtin",
            "modifiers": [(modifier, {"value": 2})],
            "output": "c",
        }

        assert func(a=1, b=2) == 3  # 1 + 2 (from modifier)

    def test_parse_ufunc(self, modifier):
        """Test the full node attributes for numpy.ufunc."""

        func_dict = parser_engine(
            "test", np.add, "c", ["a", "b"], [(modifier, {"value": 1})]
        )
        func_dict.pop("_func")

        sig = func_dict.pop("sig")

        assert list(sig.parameters) == ["a", "b"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Add arguments element-wise.",
            "functype": "numpy.ufunc",
            "modifiers": [(modifier, {"value": 1})],
            "output": "c",
        }

        assert np.array_equal(func(a=np.array([1, 2, 3]), b=2), np.array([4, 5, 6]))

    def test_parse_model(self, modifier, model_func):
        """Test the full node attributes for mmodel.model."""

        func_dict = parser_engine("test", model_func, "c", ["x", "y", "z", "xy"], [])
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

    def test_parse_callable(self, modifier, callable_func):
        """Test the full node attributes for callable."""

        func_dict = parser_engine(
            "test", callable_func, "c", ["x", "y"], [(modifier, {"value": -1})]
        )
        func_dict.pop("_func")
        sig = func_dict.pop("sig")
        assert list(sig.parameters) == ["x", "y"]

        func = func_dict.pop("func")
        assert func_dict == {
            "doc": "Sum of a and b.",
            "functype": "callable",
            "modifiers": [(modifier, {"value": -1})],
            "output": "c",
        }

        assert func(x=10, y=2) == 11
