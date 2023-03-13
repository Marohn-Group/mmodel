from mmodel.modifier import (
    loop_modifier,
    zip_loop_modifier,
    signature_modifier,
    signature_binding_modifier,
    pos_signature_modifier,
)
import pytest
import inspect


@pytest.fixture
def example_func():
    def func(a, b, c=2):
        """Test docstring"""
        return a + b + c

    return func


def test_loop(example_func):
    """Test loop modifier"""

    loop_mod = loop_modifier(example_func, "b")

    assert loop_mod(a=1, b=[1, 2, 3], c=4) == [6, 7, 8]


def test_loop_exceptions(example_func):
    """Test loop modifier exception if the input value is not an iterable"""

    loop_mod = loop_modifier(example_func, "b")

    with pytest.raises(Exception, match="b value is not iterable"):
        loop_mod(a=1, b=1, c=4)


def test_zip_loop_list(example_func):
    """Test zip loop modifier with list input"""

    loop_mod = zip_loop_modifier(example_func, ["a", "b"])

    assert loop_mod(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]


def test_signature_modifiers(example_func):
    """Test signature_modifier changes signature and executes function correctly

    Three cases are tested:
    1. len(signature_parameter) < len(func_signature)
    2. len(signature_parameter) = len(func_signature)
    """

    mod_func_1 = signature_modifier(example_func, ["d", "e"])

    # the default value is applied
    assert mod_func_1(d=1, e=2) == 5
    assert list(inspect.signature(mod_func_1).parameters.keys()) == ["d", "e"]

    mod_func_2 = signature_modifier(example_func, ["d", "e", "f"])

    assert mod_func_2(d=1, e=2, f=3) == 6
    assert list(inspect.signature(mod_func_2).parameters.keys()) == ["d", "e", "f"]


def test_signature_modifiers_kwargs():
    """Test signature modifier on function with keyword arguments

    The signature modification replaces "**kwargs" to arguments
    """

    def func(a, b, **kwargs):
        return a, b, kwargs

    mod_func = signature_modifier(func, ["e", "f", "g", "h"])

    assert mod_func(e=1, f=2, g=3, h=4) == (1, 2, {"g": 3, "h": 4})


def test_signature_modifiers_with_defaults():
    """Test signature modifier on function with keyword arguments

    The signature modification replaces "**kwargs" to arguments
    """

    def func(a, b, c):
        return a + b + c

    mod_func = signature_modifier(func, ["e", ("f", 2), "g"])

    assert mod_func(e=1, f=2, g=3) == 6
    assert mod_func(e=1, g=3) == 6


def test_pos_signature_modifiers_builtin():
    """Test pos_signature_modifiers on builtin functions"""

    import math
    import operator

    sub_mod = pos_signature_modifier(operator.sub, ["no1", "no2"])

    assert list(inspect.signature(sub_mod).parameters.keys()) == ["no1", "no2"]
    assert sub_mod(no1=2, no2=1) == 1
    # reverse wrapped input order should not affect the result
    assert sub_mod(no2=1, no1=2) == 1

    pow_mod = pos_signature_modifier(math.pow, ["no1", "no2"])

    assert list(inspect.signature(pow_mod).parameters.keys()) == ["no1", "no2"]
    assert pow_mod(no1=2, no2=1) == 2
    # reverse wrapped input order should not affect the result
    assert pow_mod(no2=2, no1=1) == 1


def test_pos_signature_modifiers_ufunc():
    """Test pos_signature_modifiers on numpy functions

    Here we test if the replacement function with different number of input parameters
    """

    import numpy as np

    arange_mod = pos_signature_modifier(np.arange, ["stop"])

    assert list(inspect.signature(arange_mod).parameters.keys()) == ["stop"]
    assert np.array_equal(arange_mod(stop=5), np.array([0, 1, 2, 3, 4]))

    arange_mod = pos_signature_modifier(np.arange, ["start", "stop"])

    assert list(inspect.signature(arange_mod).parameters.keys()) == ["start", "stop"]
    assert np.array_equal(arange_mod(start=1, stop=4), np.array([1, 2, 3]))


def test_pos_signature_modifiers_with_defaults():
    """Test signature modifier on function with keyword arguments

    The signature modification replaces "**kwargs" to arguments
    """

    import operator

    mod_func = pos_signature_modifier(operator.pow, ["e", ("power", 2)])

    assert mod_func(e=3) == 9

    mod_func = pos_signature_modifier(operator.pow, [("base", 2), "e"])

    assert mod_func(e=3) == 8


def test_signature_binding_modifier(example_func):
    """Test signature binding modifier on a regular function

    The result function should behave the same as before
    """

    mod_func = signature_binding_modifier(example_func)

    assert mod_func(1, 2) == 5
    assert mod_func(1, 2, 3) == 6
    assert mod_func(c=4, a=2, b=1) == 7

    with pytest.raises(TypeError, match="missing a required argument: 'b'"):
        mod_func(1)

    with pytest.raises(TypeError, match="got an unexpected keyword argument 'e'"):
        mod_func(a=1, b=2, e=2)


def test_signature_binding_modifier_on_wrapper(example_func):
    """Test signature binding modifier on a wrapped function

    Use signature modifier to change the function signature
    and use signature binding modifier to parse the positional and
    keyword argument input.
    """

    # the new signature is only d an e
    mod_func_1 = signature_modifier(example_func, ["d", "e"])
    mod_func_2 = signature_binding_modifier(mod_func_1)

    assert mod_func_2(1, 2) == 5
    assert mod_func_2(d=2, e=1) == 5

    with pytest.raises(TypeError, match="missing a required argument: 'e'"):
        mod_func_2(1)

    # c is not in the modified signature
    with pytest.raises(TypeError, match="got an unexpected keyword argument 'c'"):
        mod_func_2(c=4, d=2, e=1)
