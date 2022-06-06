from mmodel.modifier import (
    loop_modifier,
    zip_loop_modifier,
    signature_modifier,
    signature_binding_modifier,
)
import pytest
import inspect
from functools import wraps


@pytest.fixture
def mockedfunc():
    def func(a, b, c=2):
        """Test docstring"""
        return a + b + c

    return func


def test_loop(mockedfunc):
    """Test loop modifier"""

    loop_mod = loop_modifier("b")
    looped = loop_mod(mockedfunc)

    assert looped(a=1, b=[1, 2, 3], c=4) == [6, 7, 8]
    assert loop_mod.info == "loop_modifier(b)"

    # test the method with default
    # loop_mod = loop_modifier("c")
    # looped_default = loop_mod(mock_func)

    # assert inspect.signature(looped_default).parameters['c'].default == [2]
    # assert looped_default(a=0.1, b=0.1, c=[2]) == [2.2]
    # assert looped_default(a=0.1, b=0.1, c=[3, 4]) == [3.2, 4.2]


def test_zip_loop_list(mockedfunc):
    """Test zip loop modifier with list input"""

    loop_mod = zip_loop_modifier(["a", "b"])
    looped = loop_mod(mockedfunc)

    assert looped(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]
    assert loop_mod.info == "zip_loop_modifier(a, b)"

    # test the method with default
    # loop_mod = loop_modifier("c")
    # looped_default = loop_mod(mock_func)

    # assert inspect.signature(looped_default).parameters['c'].default == [2]
    # assert looped_default(a=0.1, b=0.1, c=[2]) == [2.2]
    # assert looped_default(a=0.1, b=0.1, c=[3, 4]) == [3.2, 4.2]


def test_zip_loop_str(mockedfunc):
    """Test zip loop modifier with string input"""

    loop_mod = zip_loop_modifier("a, b")
    looped = loop_mod(mockedfunc)

    assert looped(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]
    assert loop_mod.info == "zip_loop_modifier(a, b)"


def test_signature_modifiers(mockedfunc):
    """Test signature_modifier changes signature and executes function correctly

    Three cases are tested:
    1. len(signature_parameter) < len(func_signature)
    2. len(signature_parameter) = len(func_signature)
    """

    sig_mod_1 = signature_modifier(["d", "e"])
    mod_func_1 = sig_mod_1(mockedfunc)

    # the default value is applied
    assert mod_func_1(d=1, e=2) == 5
    assert list(inspect.signature(mod_func_1).parameters.keys()) == ["d", "e"]
    assert sig_mod_1.info == "signature_modifier(d, e)"

    sig_mod_2 = signature_modifier(["d", "e", "f"])
    mod_func_2 = sig_mod_2(mockedfunc)

    assert mod_func_2(d=1, e=2, f=3) == 6
    assert list(inspect.signature(mod_func_2).parameters.keys()) == ["d", "e", "f"]
    assert sig_mod_2.info == "signature_modifier(d, e, f)"


def test_signature_modifiers_fails(mockedfunc):
    """Test signature_modifier raises exception

    An exception is thrown when there are more parameters then the function signature
    """

    sig_mod = signature_modifier(["d", "e", "f", "g"])

    with pytest.raises(
        Exception,
        match=(
            "The number of signature modifier parameters "
            "exceeds that of function's parameters"
        ),
    ):

        sig_mod(mockedfunc)


def test_signature_binding_modifier(mockedfunc):
    """Test signature binding modifer on a regular function

    The result function should behave the same as before
    """

    sig_b_mod = signature_binding_modifier()
    assert sig_b_mod.info == "signature_binding_modifier"

    mod_func = sig_b_mod(mockedfunc)

    assert mod_func(1, 2) == 5
    assert mod_func(1, 2, 3) == 6
    assert mod_func(c=4, a=2, b=1) == 7

    with pytest.raises(TypeError, match="missing a required argument: 'b'"):
        mod_func(1)

    with pytest.raises(TypeError, match="got an unexpected keyword argument 'e'"):
        mod_func(a=1, b=2, e=2)


def test_signature_binding_modifier_on_wrapper(mockedfunc):
    """Test signature binding modifer on a wrapped function

    Use signature modifier to change the function signature
    and use signature binding modifier to parse the positional and
    keyword argument input.
    """

    # the new signature is only d an e
    sig_mod = signature_modifier(["d", "e"])
    mod_func_1 = sig_mod(mockedfunc)
    mod_func_2 = signature_binding_modifier()(mod_func_1)

    assert mod_func_2(1, 2) == 5
    assert mod_func_2(d=2, e=1) == 5

    with pytest.raises(TypeError, match="missing a required argument: 'e'"):
        mod_func_2(1)

    # c is not in the modified signature
    with pytest.raises(TypeError, match="got an unexpected keyword argument 'c'"):
        mod_func_2(c=4, d=2, e=1)
