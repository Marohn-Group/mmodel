from mmodel.modifier import (
    loop_modifier,
    zip_loop_modifier,
    signature_modifier,
    signature_binding_modifier,
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


def test_signature_modifiers_fails(example_func):
    """Test signature_modifier raises exception

    An exception is thrown when there are more parameters then the function signature
    """

    with pytest.raises(
        Exception,
        match=(
            "The number of signature modifier parameters "
            "exceeds that of function's parameters"
        ),
    ):

        signature_modifier(example_func, ["d", "e", "f", "g"])


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
