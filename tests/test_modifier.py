from mmodel.modifier import (
    loop_input,
    zip_loop_inputs,
    profile_time,
    format_time,
    add_modifier_metadata,
    format_parameters,
    print_inputs,
    print_output,
    parse_fields,
)
import pytest
import re
from inspect import signature


@pytest.fixture
def example_func():
    def func(a, b, c=2):
        """Test docstring."""
        return a + b + c

    return func


def test_parameter_stdout():
    """Test parameter_stdout modifier."""

    str_list = format_parameters(0, a="ab", b=2, c=3)
    assert str_list == ["0", "a='ab'", "b=2", "c=3"]


def test_modifier_decorator():
    """Test the modifier decorator."""

    @add_modifier_metadata("test_modifier", 1, 2, a="ab", b=2)
    def test_func(a, b):
        return a + b

    assert test_func(1, 2) == 3
    assert test_func.metadata == "test_modifier(1, 2, a='ab', b=2)"
    assert test_func.args == (1, 2)
    assert test_func.kwargs == {"a": "ab", "b": 2}


def test_modifier_metadata_immutable():
    """Test modifier metadata is immutable."""

    @add_modifier_metadata("test_modifier", 1, 2, a="ab", b=2)
    def test_func(a, b):
        return a + b

    with pytest.raises(
        TypeError, match="'mappingproxy' object does not support item assignment"
    ):
        test_func.kwargs["c"] = 3


def test_loop_input(example_func):
    """Test loop_input modifier."""

    loop_mod = loop_input("b")(example_func)

    assert "b_loop" in signature(loop_mod).parameters

    assert loop_mod(a=1, b_loop=[1, 2, 3], c=4) == [6, 7, 8]


def test_loop_metadata():
    """Test loop_input modifier metadata."""

    loop_mod = loop_input("b")

    assert loop_mod.metadata == "loop_input(parameter='b')"


def test_zip_loop_list(example_func):
    """Test zip_loop_inputs modifier with list input."""

    loop_mod = zip_loop_inputs(["a", "b"])(example_func)

    assert loop_mod(a=[0.1, 0.2, 0.3], b=[1, 2, 3], c=10) == [11.1, 12.2, 13.3]


def test_zip_loop_metadata(example_func):
    """Test zip_loop_inputs modifier metadata."""

    loop_mod = zip_loop_inputs(["a", "b"])

    assert loop_mod.metadata == "zip_loop_inputs(parameters=['a', 'b'])"


def test_format_time():
    """Test format_time function."""

    assert format_time(1e-8, 3) == "10.000 ns"
    assert format_time(1e-6, 4) == "1.0000 us"
    assert format_time(1e-2, 1) == "10.0 ms"
    assert format_time(12.2, 2) == "12.20 s"


def test_profile_time(example_func, capsys):
    """Test profile_time decorator."""

    profile_func = profile_time(2, 2, False)(example_func)

    assert profile_func(a=1, b=2, c=3) == 6
    captured = capsys.readouterr()

    pattern = r"func - 2 loops, best of 2: [0-9.e\-]+ ns|us|ms|s per loop"
    assert re.match(pattern, captured.out)


def test_profile_time_verbose(example_func, capsys):
    """Test profile_time with verbose=True decorator."""

    profile_func = profile_time(2, 2, True)(example_func)

    assert profile_func(a=1, b=2, c=3) == 6
    captured = capsys.readouterr()
    pattern = r"func - raw times: \[[0-9.e\-]+, [0-9.e\-]+\]"

    assert re.match(pattern, captured.out) is not None


class TestPrintModifiers:
    @pytest.fixture
    def func(self):
        def b_tot(b1, b0, bz):
            return b1 + b0 + bz

        return b_tot

    def test_parse_field_with_attributes_or_slicers(self):
        """Test the parse_field that can parse field with attributes or slicers."""

        assert sorted(parse_fields("{b0[0]} [mT] b0 {b0[1]:.3e} [mT] {b1.value}")) == [
            "b0",
            "b1",
        ]

    def test_parse_field(self):
        """Test the parse_field function."""

        assert sorted(
            parse_fields("b1 {b1:.3f} [mT] b0 {b0:.3e} [mT] bz {bz} [mT]")
        ) == [
            "b0",
            "b1",
            "bz",
        ]

    def test_print_inputs(self, capsys, func):
        """Test the print_inputs."""

        mod = print_inputs("b1 {b1:.3f} [mT] b0 {b0:.3e} [mT] bz {bz}", end="--")
        mod_func = mod(func)
        mod_func(b1=1, b0=2, bz=3)
        captured = capsys.readouterr()
        assert captured.out == "b1 1.000 [mT] b0 2.000e+00 [mT] bz 3--"
        assert (
            mod.metadata == "print_inputs(format_str='b1 {b1:.3f} "
            "[mT] b0 {b0:.3e} [mT] bz {bz}', end='--')"
        )

    def test_print_output_modifier(self, capsys, func):
        """Test the stdout_output_modifier."""

        mod = print_output("b_tot {b_tot:.1f} [mT]")
        mod_func = mod(func)
        mod_func(b1=1, b0=2, bz=3)
        captured = capsys.readouterr()
        assert captured.out == "b_tot 6.0 [mT]\n"
        assert mod.metadata == "print_output(format_str='b_tot {b_tot:.1f} [mT]')"
