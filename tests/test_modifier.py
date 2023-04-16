from mmodel.modifier import (
    loop_input,
    zip_loop_inputs,
    redefine_signature,
    redefine_pos_signature,
    bind_signature,
    profile_time,
    format_time,
)
import pytest
import inspect
import re


@pytest.fixture
def example_func():
    def func(a, b, c=2):
        """Test docstring."""
        return a + b + c

    return func


def test_loop_input(example_func):
    """Test loop_input modifier."""

    loop_mod = loop_input("b")(example_func)

    assert loop_mod(a=1, b=[1, 2, 3], c=4) == [6, 7, 8]


def test_loop_exceptions(example_func):
    """Test loop_input modifier exception if the input value is not iterable."""

    loop_mod = loop_input("b")(example_func)

    with pytest.raises(Exception, match="b value is not iterable"):
        loop_mod(a=1, b=1, c=4)


def test_loop_metadata(example_func):
    """Test loop_input modifier metadata."""

    loop_mod = loop_input("b")

    assert loop_mod.metadata == "loop_input('b')"


def test_zip_loop_list(example_func):
    """Test zip_loop_inputs modifier with list input."""

    loop_mod = zip_loop_inputs(["a", "b"])(example_func)

    assert loop_mod(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]


def test_zip_loop_metadata(example_func):
    """Test zip_loop_inputs modifier metadata."""

    loop_mod = zip_loop_inputs(["a", "b"])

    assert loop_mod.metadata == "zip_loop(['a', 'b'])"


def test_redefine_signature(example_func):
    """Test redefine_signature changes signature and executes function correctly.

    Three cases are tested:
    1. len(signature_parameter) < len(func_signature)
    2. len(signature_parameter) = len(func_signature)
    """

    mod_func_1 = redefine_signature(["d", "e"])(example_func)

    # the default value is applied
    assert mod_func_1(d=1, e=2) == 5
    assert list(inspect.signature(mod_func_1).parameters.keys()) == ["d", "e"]

    mod_func_2 = redefine_signature(["d", "e", "f"])(example_func)

    assert mod_func_2(d=1, e=2, f=3) == 6
    assert list(inspect.signature(mod_func_2).parameters.keys()) == ["d", "e", "f"]


def test_redefine_signatures_kwargs():
    """Test signature modifier on function with keyword arguments.

    The signature modification replaces "**kwargs" with arguments.
    """

    def func(a, b, **kwargs):
        return a, b, kwargs

    mod_func = redefine_signature(["e", "f", "g", "h"])(func)

    assert mod_func(e=1, f=2, g=3, h=4) == (1, 2, {"g": 3, "h": 4})


def test_redefine_signature_with_defaults():
    """Test signature modifier on function with keyword arguments.

    The signature modification replaces "**kwargs" with arguments.
    """

    def func(a, b, c):
        return a + b + c

    mod_func = redefine_signature(["e", ("f", 2), "g"])(func)

    assert mod_func(e=1, f=2, g=3) == 6
    assert mod_func(e=1, g=3) == 6


def test_redefine_pos_signature_builtin():
    """Test pos_replace_signature on builtin functions."""

    import math
    import operator

    sub_mod = redefine_pos_signature(["no1", "no2"])(operator.sub)

    assert list(inspect.signature(sub_mod).parameters.keys()) == ["no1", "no2"]
    assert sub_mod(no1=2, no2=1) == 1
    # reverse wrapped input order should not affect the result
    assert sub_mod(no2=1, no1=2) == 1

    pow_mod = redefine_pos_signature(["no1", "no2"])(math.pow)

    assert list(inspect.signature(pow_mod).parameters.keys()) == ["no1", "no2"]
    assert pow_mod(no1=2, no2=1) == 2
    # reverse wrapped input order should not affect the result
    assert pow_mod(no2=2, no1=1) == 1


def test_redefine_pos_signatures_ufunc():
    """Test redefine_pos_signature on numpy.ufunc.

    Test if the replacement function with a different number of input parameters.
    """

    import numpy as np

    arange_mod = redefine_pos_signature(["stop"])(np.arange)

    assert list(inspect.signature(arange_mod).parameters.keys()) == ["stop"]
    assert np.array_equal(arange_mod(stop=5), np.array([0, 1, 2, 3, 4]))

    arange_mod = redefine_pos_signature(["start", "stop"])(np.arange)

    assert list(inspect.signature(arange_mod).parameters.keys()) == ["start", "stop"]
    assert np.array_equal(arange_mod(start=1, stop=4), np.array([1, 2, 3]))


def test_redefine_pos_signature_with_defaults():
    """Test signature modifier on function with keyword arguments.

    The signature modification replaces "**kwargs" with arguments.
    """

    import operator

    mod_func = redefine_pos_signature(["e", ("power", 2)])(operator.pow)

    assert mod_func(e=3) == 9

    mod_func = redefine_pos_signature([("base", 2), "e"])(operator.pow)

    assert mod_func(e=3) == 8


def test_signature_binding_modifier(example_func):
    """Test signature binding modifier on a regular function.

    The result function should behave the same as before.
    """

    mod_func = bind_signature(example_func)

    assert mod_func(1, 2) == 5
    assert mod_func(1, 2, 3) == 6
    assert mod_func(c=4, a=2, b=1) == 7

    with pytest.raises(TypeError, match="missing a required argument: 'b'"):
        mod_func(1)

    with pytest.raises(TypeError, match="got an unexpected keyword argument 'e'"):
        mod_func(a=1, b=2, e=2)


def test_signature_binding_modifier_on_wrapper(example_func):
    """Test signature binding modifier on a wrapped function.

    Use signature modifier to change the function signature
    and use the signature binding modifier to parse the positional and
    keyword argument input.
    """

    # the new signature is only d an e
    mod_func_1 = redefine_signature(["d", "e"])(example_func)
    mod_func_2 = bind_signature(mod_func_1)

    assert mod_func_2(1, 2) == 5
    assert mod_func_2(d=2, e=1) == 5

    with pytest.raises(TypeError, match="missing a required argument: 'e'"):
        mod_func_2(1)

    # c is not in the modified signature
    with pytest.raises(TypeError, match="got an unexpected keyword argument 'c'"):
        mod_func_2(c=4, d=2, e=1)


def test_format_time():
    """Test format_time function."""

    assert format_time(1e-8, 3) == "10.000 ns"
    assert format_time(1e-6, 4) == "1.0000 us"
    assert format_time(1e-2, 1) == "10.0 ms"
    assert format_time(12.2, 2) == "12.20 s"


def test_profile_time(example_func, capsys):
    """Test profile_time decorator."""

    profile_func = profile_time(2, 2, False)(example_func)

    assert profile_func(1, 2, 3) == 6
    captured = capsys.readouterr()

    pattern = r"func - 2 loops, best of 2: [0-9.e\-]+ ns|us|ms|s per loop"
    assert re.match(pattern, captured.out)


def test_profile_time_verbose(example_func, capsys):
    """Test profile_time with verbose=True decorator."""

    profile_func = profile_time(2, 2, True)(example_func)

    assert profile_func(1, 2, 3) == 6
    captured = capsys.readouterr()
    pattern = r"func - raw times: \[[0-9.e\-]+, [0-9.e\-]+\]"

    assert re.match(pattern, captured.out) is not None
