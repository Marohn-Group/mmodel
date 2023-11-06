from mmodel import Node
import pytest
from inspect import Signature, Parameter
from textwrap import dedent
import numpy as np


@pytest.fixture
def func():
    def func_a(m, n):
        """Base function."""
        return m + n

    return func_a


class TestSetNodeObject:
    """Test set_node_object and set_node_objects_from."""

    @pytest.fixture
    def node(self, func, value_modifier):
        """Basic Graph with pre-defined edges."""

        node_a = Node(
            "func_a",
            func,
            output="o",
            inputs=["a", "b"],
            modifiers=[value_modifier(value=1)],
            add_attr="additional attribute",
        )

        return node_a

    def test_attributes(self, node):
        """Test node object."""

        assert node.name == "func_a"
        assert node.__name__ == "func_a"
        assert node.func(1, 2) == 3
        assert node.node_func(1, 2) == 4
        assert node(1, 2) == 4
        assert node.output == "o"
        assert node.inputs == ["a", "b"]
        assert (
            node.modifiers[0].__qualname__
            == "value_modifier.<locals>.add_value.<locals>.mod"
        )
        assert list(node.signature.parameters.keys()) == ["a", "b"]
        assert node.functype == "function"
        assert node.__signature__ == node.signature
        assert node.doc == "Base function."
        assert node.add_attr == "additional attribute"

    def test_str_representation(self, node):
        """Test if view node outputs node information correctly."""

        node_s = """\
        func_a

        func_a(a, b)
        return: o
        functype: function
        modifiers:
        - add_value(value=1)

        Base function."""

        assert str(node) == dedent(node_s)

    def test_edit(self, node):
        """Test edit node."""

        new_node = node.edit(
            func=np.min, output="new_o", inputs=["array"], doc="new doc"
        )

        assert new_node.output == "new_o"
        assert new_node.inputs == ["array"]
        assert new_node([5, 20]) == 6  # the modifier is the same
        assert new_node.add_attr == "additional attribute"
        assert new_node.doc == "new doc"
        print(type(new_node.func))
        assert new_node.functype == "numpy._ArrayFunctionDispatcher"

    def test_node_property(self, node):
        """Test if node modifiers and inputs are copies.

        Modification to these attributes should not affect the original node.
        """

        assert node.modifiers is not node.modifiers
        node.modifiers.append(1)
        assert len(node.modifiers) == 1

        assert node.inputs is not node.inputs
        node.inputs.append("f")
        assert node.inputs == ["a", "b"]


class TestNodeConstruction:
    """Test node construction."""

    def test_additional_kwargs(self, func):
        """Test additional kwargs are added to the node.

        The additional kwargs override the node attributes.
        """

        new_node_obj = Node(
            "func_a", func, output="o", inputs=["a", "b"], foo="bar", doc="foo"
        )

        assert new_node_obj.foo == "bar"
        assert new_node_obj.doc == "foo"

    def test_lambda_as_function(self):
        """Test node object input for lambda function.

        Test the result alongside the base parser test to see if
        the lambda doc is parsed correctly.
        """
        node_a = Node("func_a", lambda x: (x[2]), output="o")
        assert node_a.doc == None

    def test_function_without_input(self):
        """Test node object input for function with no input.

        Test the result alongside the base parser test to see if
        the lambda doc is parsed correctly.
        """

        def func_a():
            """Return 1."""
            return 1

        node_a = Node("func_a", func_a, output="o")

        assert node_a.signature == Signature()

    def test_node_metadata_with_no_returns(self):
        """If the node doesn't have returns, metadata should output None."""

        node = Node("Test", lambda x: None)

        node_s = """\
        Test

        <lambda>(x)
        return: None
        functype: function"""

        assert str(node) == dedent(node_s)


class TestSignatureModification:
    """Test node object input for builtin func and ufunc."""

    def test_builtin_func(self):
        """Test node object input for builtin func."""

        node = Node("Test", sum, ["iters"])

        doc = """\
        Return the sum of a 'start' value (default: 0) plus an iterable of numbers

        When the iterable is empty, return the start value.
        This function is intended specifically for use with numeric values and may
        reject non-numeric types."""

        assert node.signature == Signature(
            parameters=[Parameter("iters", Parameter.POSITIONAL_OR_KEYWORD)]
        )
        assert node([1, 2]) == 3
        assert node.doc == dedent(doc)

    def test_ufunc(self):
        """Test node object input for builtin func."""

        node = Node("Test", np.sum, ["array"])

        assert node.signature == Signature(
            parameters=[Parameter("array", Parameter.POSITIONAL_OR_KEYWORD)]
        )
        assert node([1, 2]) == 3
        assert "Sum of array elements over a given axis." in node.doc

    def test_signature_less_exception(self):
        """Test exception when a node does not have inputs defined."""

        with pytest.raises(
            Exception, match="node 'Test' function requires 'inputs' to be specified"
        ):
            Node("Test", np.add)
