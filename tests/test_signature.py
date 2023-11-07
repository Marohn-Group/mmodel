from mmodel.signature import (
    split_arguments,
    convert_signature,
    add_signature,
    modify_signature,
    restructure_signature,
    has_signature,
    check_signature,
)
from inspect import signature, Parameter
import pytest
import operator
import numpy as np
import math


def tfunc(a, b, /, c, d, *, e, f=2, **kwargs):
    """The test function.

    The test has 2 position-only and 2 keyword-only arguments.
    The last parameter has a default value.
    """
    return a + b + c + d + e + f + sum(kwargs.values())


def test_split_arguments():
    """Test the split_arguments function."""

    sig = signature(tfunc)
    arguments = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6}

    args, kwargs = split_arguments(sig, arguments)

    assert args == [1, 2]
    assert kwargs == {"c": 3, "d": 4, "e": 5, "f": 6}


def test_modify_signature():
    """Test the modify_signature function."""

    new_func = modify_signature(tfunc, ["a1", "b1", "c1", "d1", "e1", "f1"])

    assert list(signature(new_func).parameters.keys()) == [
        "a1",
        "b1",
        "c1",
        "d1",
        "e1",
        "f1",
    ]

    assert new_func(a1=1, b1=2, c1=3, d1=4, e1=5, f1=6) == 21


def test_modify_signature_without_default():
    """Test the modify_signature function."""

    new_func = modify_signature(tfunc, ["a1", "b1", "c1", "d1", "e1"])

    assert list(signature(new_func).parameters.keys()) == ["a1", "b1", "c1", "d1", "e1"]
    assert new_func(a1=1, b1=2, c1=3, d1=4, e1=5) == 17

    with pytest.raises(TypeError, match="got an unexpected keyword argument 'f1'"):
        new_func(a1=1, b1=2, c1=3, d1=4, e1=5, f1=6)


def test_modify_signature_with_added_keywords():
    """Test the signature can replace the kwargs."""

    new_func = modify_signature(tfunc, ["a", "b", "c", "d", "e", "f", "g"])

    assert list(signature(new_func).parameters.keys()) == [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
    ]
    assert new_func(a=1, b=2, c=3, d=4, e=5, f=6, g=7) == 28


def test_modify_signature_inputs_number():
    """Test if the given inputs are not enough, the function raises exception."""

    def func(a, b, c=3):
        return a + b + c

    assert list(signature(modify_signature(func, ["a", "b"])).parameters.keys()) == [
        "a",
        "b",
    ]

    assert list(
        signature(modify_signature(func, ["a", "b", "c"])).parameters.keys()
    ) == ["a", "b", "c"]

    with pytest.raises(ValueError, match="Too many inputs for the function"):
        modify_signature(func, ["a", "b", "c", "d"])

    with pytest.raises(ValueError, match="Not enough inputs for the function"):
        modify_signature(tfunc, ["a", "b", "c", "d"])


def test_modify_signature_pos_expand():
    """Test if the given inputs are not enough, the function raises exception."""

    def func(a, b, c=3, /, d=4, *args):
        return a + b + c + d + sum(args)

    mod_func = modify_signature(func, ["a", "b", "c", "d", "e", "f"])
    assert mod_func(1, 2, 3, 4, 5, 6) == 21

    mod_func = modify_signature(func, ["a", "b"])
    assert mod_func(1, 2) == 10

    with pytest.raises(ValueError, match="Not enough inputs for the function"):
        modify_signature(tfunc, ["a"])


def test_modify_signature_with_kw_only():
    """Test if the given inputs are not enough, the function raises exception."""

    def func(a, b, c=3, /, d=4, *args, f=5):
        return a + b + c + d + sum(args) - f

    mod_func = modify_signature(func, ["a", "b", "c", "d", "f"])
    print(signature(mod_func))
    assert mod_func(1, 2, 3, 4, 6) == 4

    # mod_func = modify_signature(func, ["a", "b"])
    # assert mod_func(1, 2) == 10

    # with pytest.raises(ValueError, match="Not enough inputs for the function"):
    #     modify_signature(tfunc, ["a"])

def test_convert_signature():
    """Test the convert_signature function."""

    new_func = convert_signature(tfunc)

    # make sure all arguments are keyword and position only
    sig = signature(new_func)

    assert list(sig.parameters.keys()) == ["a", "b", "c", "d", "e"]

    for param in list(sig.parameters.values())[:-1]:
        assert param.kind == Parameter.POSITIONAL_OR_KEYWORD

    # e is keyword only
    assert sig.parameters["e"].kind == Parameter.KEYWORD_ONLY

    # only keyword
    assert new_func(a=1, b=2, c=3, d=4, e=5) == 17
    assert new_func(1, 2, 3, 4, e=5) == 17

    # check it removes the default signature
    with pytest.raises(TypeError, match="got an unexpected keyword argument 'f'"):
        new_func(a=1, b=2, c=3, d=4, e=5, f=6)


def test_convert_signature_with_pre_defined():
    """Test the convert_signature function with pre-defined functions."""

    new_add = convert_signature(operator.add)

    for param in signature(new_add).parameters.values():
        assert param.kind == Parameter.POSITIONAL_OR_KEYWORD

    assert new_add(a=1, b=2) == 3
    assert new_add(1, 2) == 3


def test_add_signature():
    """Test the add_signature function."""

    new_add = add_signature(np.add, ["first", "second"])

    for param in signature(new_add).parameters.values():
        assert param.kind == Parameter.POSITIONAL_OR_KEYWORD

    assert new_add(first=1, second=2) == 3

    new_sqrt = add_signature(math.sqrt, ["x"])

    for param in signature(new_sqrt).parameters.values():
        assert param.kind == Parameter.POSITIONAL_OR_KEYWORD

    assert new_sqrt(x=4) == 2


def test_restructure_signature():
    """Test the restructure_signature function."""

    def testfunc(a, b, c, e):
        return a + b + c + e

    sig = signature(testfunc)
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


def test_has_signature():
    """Test the has_signature function."""

    assert has_signature(tfunc)
    assert not has_signature(np.add)
    assert has_signature(np.sum)
    assert has_signature(operator.add)
    assert has_signature(math.sqrt)
    assert not has_signature(math.log)


def test_check_signature():
    """Test the check_signature function."""

    def func(a, *, b):
        return

    assert check_signature(func)
    assert not check_signature(tfunc)
    assert not check_signature(np.sum)
    assert not check_signature(operator.add)
    assert not check_signature(math.sqrt)
