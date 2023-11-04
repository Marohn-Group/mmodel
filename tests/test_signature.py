from mmodel.signature import (
    split_arguments,
    convert_signature,
    add_signature,
    add_defaults,
)
from inspect import signature
import pytest
import operator
import numpy as np
import math


def tfunc(a, b, /, c, d, *, e, f=2):
    """The test function.

    The test has 2 position only and 2 keyword only arguments.
    The last variable has a default value.
    """
    return


def test_split_arguments():
    """Test the split_arguments function."""

    sig = signature(tfunc)
    arguments = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6}

    args, kwargs = split_arguments(sig, arguments)

    assert args == [1, 2]
    assert kwargs == {"c": 3, "d": 4, "e": 5, "f": 6}


def test_convert_signature():
    """Test the convert_signature function."""

    new_func = convert_signature(tfunc)

    # only keyword
    assert new_func(a=1, b=2, c=3, d=4, e=5, f=6) is None
    # only positional
    assert new_func(1, 2, 3, 4, 5, 6) is None

    # test it removes the default value
    with pytest.raises(TypeError, match="missing a required argument: 'f'"):
        new_func(1, 2, 3, 4, 5)

    # make sure all arguments are keyword and position only
    sig = signature(new_func)
    for param in sig.parameters.values():
        assert param.kind == 1


def test_convert_signature_with_pre_defined():
    """Test the convert_signature function with pre-defined functions."""

    new_add = convert_signature(operator.add)

    for param in signature(new_add).parameters.values():
        assert param.kind == 1

    assert new_add(a=1, b=2) == 3
    assert new_add(1, 2) == 3


def test_add_signature():
    """Test the add_signature function."""

    new_add = add_signature(np.add, ["first", "second"])

    for param in signature(new_add).parameters.values():
        assert param.kind == 1

    assert new_add(first=1, second=2) == 3
    assert new_add(1, 2) == 3

    new_sqrt = add_signature(math.sqrt, ["x"])

    for param in signature(new_sqrt).parameters.values():
        assert param.kind == 1

    assert new_sqrt(x=4) == 2
    assert new_sqrt(4) == 2


def test_add_defaults():
    """Test the add_defaults function."""

    sig = signature(tfunc)
    default_dict = {"e": 3}

    new_sig = add_defaults(sig, default_dict)

    assert new_sig.parameters["e"].default == 3
    assert new_sig.parameters["e"].kind == 1

    # check the new order
    assert list(new_sig.parameters.keys()) == ["a", "b", "c", "d", "f", "e"]

    bound = new_sig.bind(1, 2, 3, 4, 5)
    bound.apply_defaults()
    assert bound.arguments["e"] == 3
