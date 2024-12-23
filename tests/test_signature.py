from mmodel.signature import (
    restructure_signature,
    get_node_signature,
    get_parameters,
    check_kwargs,
    check_args,
    convert_func,
)
from inspect import signature, Parameter, Signature
import pytest
import numpy as np


def test_get_param_dict_with_sig():
    """Test the get_param_dict function on function with signature."""

    def test_func(a, /, b, *args, c=2, **kwargs):
        """The test function.

        The test has two position-only and two keyword-only arguments.
        The last parameter has a default value.
        """
        return a + b + c + sum(args) + sum(kwargs.values())

    params = get_parameters(test_func)
    assert params == [
        Parameter("a", 0),
        Parameter("b", 1),
        Parameter("args", 2),
        Parameter("c", 3, default=2),
        Parameter("kwargs", 4),
    ]


def test_get_param_dict_without_sig():
    """Test the get_param_dict function on built-in function."""

    params = get_parameters(zip)
    assert params == [Parameter("args", 2), Parameter("kwargs", 4)]


class TestNodeSignature:
    """Test the node argument inputs and signature-related functions.

    Exception matches use regex is due to set does not preserve order.
    """

    @pytest.fixture
    def param_set1(self):
        """Return a set of var- and regular parameters."""
        return [
            Parameter("pos_only", 0),
            Parameter("pos_or_kw", 1),
            Parameter("var_pos", 2),
            Parameter("kw_only", 3),
            Parameter("var_kw", 4),
        ]

    @pytest.fixture
    def param_set2(self):
        """Return a set of regular parameters."""
        return [
            Parameter("pos_only", 0),
            Parameter("pos_or_kw", 1),
            Parameter("kw_only", 3),
        ]

    @pytest.fixture
    def param_set3(self):
        """Return a set of default parameters."""
        return [
            Parameter("pos_only", 0),
            Parameter("pos_or_kw1", 1),
            Parameter("pos_or_kw2", 1, default=1),
            Parameter("kw_only1", 3),
            Parameter("kw_only2", 3),
            Parameter("kw_only3", 3, default=3),
        ]

    @pytest.fixture
    def param_set4(self):
        """Return a set of var- parameters."""
        return [
            Parameter("var_pos", 2),
            Parameter("var_kw", 4),
        ]

    def test_check_args_with_var_pos(self, param_set1):
        """Test the check_args function with var_pos in sigature."""

        # regular replacement
        assert check_args(param_set1, ["a", "b"])
        # allow for more than 2 parameters with var_pos
        assert check_args(param_set1, ["a", "b", "c"])

        # check minimum length
        with pytest.raises(Exception, match="not enough positional arguments"):
            check_args(param_set1, ["pos_only"])

    def test_check_args_without_var_pos(self, param_set2):
        """Test the check_args function without var_pos in signature."""

        # regular replacement
        assert check_args(param_set2, ["a", "b"])
        # not allow more than 2 parameters
        with pytest.raises(Exception, match="too many positional arguments"):
            assert check_args(param_set2, ["a", "b", "c"])

        # check minimum length
        with pytest.raises(Exception, match="not enough positional arguments"):
            check_args(param_set2, ["pos_only"])

    def test_check_args_with_defaults(self, param_set3):
        """Test the check_args function with default positional arguments."""

        # allow for 3 arguments even with default values
        assert check_args(param_set3, ["a", "b", "c"])
        # allow for 2 arguments due to one default value
        assert check_args(param_set3, ["a", "b"])

        # check minimum length
        with pytest.raises(Exception, match="not enough positional arguments"):
            check_args(param_set3, ["a"])

    def test_check_args_with_var_pos_only(self, param_set4):
        """Test the check_args function with only var_pos in signature."""

        # allow for multiple arguments
        assert check_args(param_set4, ["a", "b"])
        # allow for empty argument list
        assert check_args(param_set4, [])

    def test_check_kwargs_with_var_kw(self, param_set1):
        """Test the check_kwargs function."""
#               Parameter("pos_only", 0),
#             Parameter("pos_or_kw", 1),
#             Parameter("var_pos", 2),
#             Parameter("kw_only", 3),
#             Parameter("var_kw", 4),


        # regular replacement with the same name
        assert check_kwargs(param_set1, ["kw_only"])
        # allow for other keyword arguments with var_kw
        assert check_kwargs(param_set1, ["kw_only", "a", "b"])


        # check the minimum length
        with pytest.raises(
            Exception, match=r"not enough keyword arguments, minimum 1 but got 0"
        ):
            check_kwargs(param_set1, [])

    def test_check_kwargs_without_var_kw(self, param_set2):

        # regular replacement
        assert check_kwargs(param_set2, ["kw_only"])
        # not allow more than 2 parameters
        with pytest.raises(
            Exception, match=r"too many keyword arguments, maximum 1 but got 3"
        ):
            assert check_kwargs(param_set2, ["kw_only", "a", "b"])

        # check the minimum length
        with pytest.raises(
            Exception, match=r"not enough keyword arguments, minimum 1 but got 0"
        ):
            check_kwargs(param_set2, [])

    def test_check_kwargs_with_defaults(self, param_set3):

        # allow for 2 arguments even with default values
        assert check_kwargs(param_set3, ["kw_only1", "kw_only2", "kw_only3"])
        # allow for 1 arguments due to one default value
        assert check_kwargs(param_set3, ["kw_only1", "kw_only2"])

        # check the minimum length
        with pytest.raises(
            Exception, match=r"not enough keyword arguments, minimum 2 but got 1"
        ):
            check_kwargs(param_set3, ["a"])

        # check the maximum length
        with pytest.raises(
            Exception,
            match=r"too many keyword arguments, maximum 3 but got 4"
        ):
            check_kwargs(param_set3, ["a", "b", "c", "d"])

    def test_check_kwargs_with_var_kw_only(self, param_set4):
        """Test the check_kwargs function with only var_kw in signature."""

        # allow for multiple arguments
        assert check_kwargs(param_set4, ["a", "b"])
        # allow for empty argument list
        assert check_kwargs(param_set4, [])

    def test_get_node_signature_without_arugment_lists(
        self, param_set1, param_set2, param_set3, param_set4
    ):
        """Test the get_node_signature function."""

        assert get_node_signature(param_set1, []) == Signature(
            [
                Parameter("pos_only", 0),
                Parameter("pos_or_kw", 1),
                Parameter("kw_only", 3),
            ]
        )

        assert get_node_signature(param_set2, []) == Signature(
            [
                Parameter("pos_only", 0),
                Parameter("pos_or_kw", 1),
                Parameter("kw_only", 3),
            ]
        )

        assert get_node_signature(param_set3, []) == Signature(
            [
                Parameter("pos_only", 0),
                Parameter("pos_or_kw1", 1),
                Parameter("kw_only1", 3),
                Parameter("kw_only2", 3),
            ]
        )

        assert get_node_signature(param_set4, []) == Signature()

    def test_get_node_signature_with_arugment_lists(
        self, param_set1, param_set2, param_set3, param_set4
    ):
        """Test the get_node_signature function with argument lists."""

        assert get_node_signature(
            param_set1, ["a", "b", "c", "*", "kw_only", "d"]
        ) == Signature(
            [
                Parameter("a", 1),
                Parameter("b", 1),
                Parameter("c", 1),
                Parameter("kw_only", 3),
                Parameter("d", 3),
            ]
        )

        assert get_node_signature(param_set2, ["a", "b", "*", "kw_only"]) == Signature(
            [
                Parameter("a", 1),
                Parameter("b", 1),
                Parameter("kw_only", 3),
            ]
        )

        assert get_node_signature(
            param_set3, ["a", "b", "*", "kw_only1", "kw_only2"]
        ) == Signature(
            [
                Parameter("a", 1),
                Parameter("b", 1),
                Parameter("kw_only1", 3),
                Parameter("kw_only2", 3),
            ]
        )

        assert get_node_signature(
            param_set3, ["a", "b", "c", "*", "kw_only1", "kw_only2", "kw_only3"]
        ) == Signature(
            [
                Parameter("a", 1),
                Parameter("b", 1),
                Parameter("c", 1),
                Parameter("kw_only1", 3),
                Parameter("kw_only2", 3),
                Parameter("kw_only3", 3),
            ]
        )

        assert get_node_signature(param_set4, ["a", "b", "*", "c", "d"]) == Signature(
            [
                Parameter("a", 1),
                Parameter("b", 1),
                Parameter("c", 3),
                Parameter("d", 3),
            ]
        )


def test_convert_func():
    """Test the convert_func function in and out of order."""

    def test_func1(a, /, b, *args, c=2, **kwargs):
        return a + b - c + np.sum(args) + np.prod(list(kwargs.values()))

    sig = Signature(
        [
            Parameter("a", 0),
            Parameter("b", 1),
            Parameter("d", 1),
            Parameter("e", 1),
            Parameter("f", 3),
            Parameter("g", 3),
        ]
    )

    # a, b, d, e are positional-only
    new_func = convert_func(test_func1, sig)
    assert new_func.__signature__ == sig
    assert signature(new_func) == sig
    assert new_func(a=1, b=2, d=4, e=5, f=6, g=7) == 52
    assert new_func(b=2, d=4, e=5, a=1, f=6, g=7) == 52

    sig = Signature(
        [
            Parameter("a", 0),
            Parameter("b", 1),
            Parameter("d", 3),
            Parameter("e", 3),
            Parameter("f", 3),
            Parameter("g", 3),
        ]
    )

    # a, b are positional-only
    new_func = convert_func(test_func1, sig)
    assert new_func(a=1, b=2, d=4, e=5, f=6, g=7) == 841
    assert new_func(f=6, g=7, a=1, b=2, d=4, e=5) == 841

    sig = Signature(
        [
            Parameter("a", 0),
            Parameter("b", 1),
            Parameter("d", 1),
            Parameter("c", 3),
            Parameter("e", 3),
            Parameter("g", 3),
        ]
    )

    # a, b, d are positional
    # c is keyword-only
    new_func = convert_func(test_func1, sig)
    assert new_func(a=1, b=2, d=4, c=5, e=6, g=7) == 44
    assert new_func(a=1, c=5, e=6, b=2, d=4, g=7) == 44


def test_convert_func_exception():
    """Test when the converted function shows the correct exception."""

    def test_func1(a, b, c):
        return a + b - c

    sig = Signature([Parameter("a", 0), Parameter("b", 1), Parameter("c", 1)])

    new_func = convert_func(test_func1, sig)
    with pytest.raises(TypeError, match="missing a required argument: 'c'"):
        new_func(a=1, b=2)


def test_restructure_signature():
    """Test the restructure_signature function."""

    def test_func(a, b, c, e):
        return a + b + c + e

    sig = signature(test_func)
    default_dict = {"c": 3}

    new_sig = restructure_signature(sig, default_dict)

    assert new_sig.parameters["c"].default == 3
    assert new_sig.parameters["c"].kind == Parameter.POSITIONAL_OR_KEYWORD

    # check the new order
    assert list(new_sig.parameters.keys()) == ["a", "b", "e", "c"]

    bound = new_sig.bind(a=1, b=2, e=3)
    bound.apply_defaults()
    assert bound.arguments["c"] == 3

    bound = new_sig.bind(a=1, b=2, e=3, c=5)
    bound.apply_defaults()
    assert bound.arguments["c"] == 5
