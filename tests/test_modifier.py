from mmodel.modifier import basic_loop, zip_loop
import pytest

@pytest.fixture
def mockedfunc():
    def func(a, b, c=2):
        """Test docstring"""
        return a + b + c

    return func

def test_basic_loop(mockedfunc):
    """Test redirect edges based on subgraph and subgraph node"""

    loop_mod = basic_loop("b")
    looped = loop_mod(mockedfunc)

    assert looped(a=1, b=[1, 2, 3], c=4) == [6, 7, 8]

    # test the method with default
    # loop_mod = basic_loop("c")
    # looped_default = loop_mod(mock_func)

    # assert inspect.signature(looped_default).parameters['c'].default == [2]
    # assert looped_default(a=0.1, b=0.1, c=[2]) == [2.2]
    # assert looped_default(a=0.1, b=0.1, c=[3, 4]) == [3.2, 4.2]


def test_zip_loop(mockedfunc):
    """Test redirect edges based on subgraph and subgraph node"""

    loop_mod = zip_loop(["a", "b"])
    looped = loop_mod(mockedfunc)

    assert looped(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]

    # test the method with default
    # loop_mod = basic_loop("c")
    # looped_default = loop_mod(mock_func)

    # assert inspect.signature(looped_default).parameters['c'].default == [2]
    # assert looped_default(a=0.1, b=0.1, c=[2]) == [2.2]
    # assert looped_default(a=0.1, b=0.1, c=[3, 4]) == [3.2, 4.2]
