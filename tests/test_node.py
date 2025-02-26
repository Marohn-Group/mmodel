from mmodel import Node, Model, BasicHandler
import pytest
from inspect import Signature, Parameter
from textwrap import dedent
import numpy as np
import math


@pytest.fixture
def func():
    def func_a(m, n, *, c=0):
        """Base function."""
        return m + n - c

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
            inputs=["a", "b", "*", "c"],
            modifiers=[value_modifier(value=1)],
            add_attr="additional attribute",
        )

        return node_a

    def test_attributes(self, node):
        """Test node object."""

        assert node.name == "func_a"
        assert node.__name__ == "func_a"
        # original function
        assert node.func(1, 2, c=3) == 0
        assert node._base_func(a=1, b=2, c=3) == 0
        # modified function + 1 in value
        assert node.node_func(a=1, b=2, c=3) == 1  # kw only
        assert node(1, 2, c=3) == 1
        assert node.output == "o"
        assert node.inputs == ["a", "b", "*", "c"]
        assert (
            node.modifiers[0].__qualname__
            == "value_modifier.<locals>.add_value.<locals>.mod"
        )
        assert list(node.signature.parameters.keys()) == ["a", "b", "c"]
        assert node.functype == "function"
        assert node.__signature__ == node.signature
        assert node.doc == "Base function."
        assert node.add_attr == "additional attribute"
        assert repr(node) == "<mmodel.node.Node 'func_a'>"

    def test_str_representation(self, node):
        """Test if view node outputs node information correctly."""

        node_s = """\
        func_a

        func_a(a, b, *, c)
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
        assert node.inputs == ["a", "b", "*", "c"]


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

    def test_node_callable(self):
        """Test the node callable checks the input correctly."""

        node = Node("Test", lambda x: x)
        with pytest.raises(TypeError, match="too many positional arguments"):
            node(1, 2)

        with pytest.raises(TypeError, match="missing a required argument: 'x'"):
            node()

        with pytest.raises(TypeError, match="got an unexpected keyword argument 'y'"):
            node(x=1, y=4)


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

        assert node.signature == Signature(parameters=[Parameter("iters", 1)])
        assert node([1, 2]) == 3
        assert node.doc == dedent(doc)

    def test_ufunc(self):
        """Test node object argument_list for builtin func."""

        node = Node("Test", np.sum, ["array"])

        assert node.signature == Signature(parameters=[Parameter("array", 1)])
        assert node([1, 2]) == 3
        assert "Sum of array elements over a given axis." in node.doc

    def test_ufunc_with_keyword(self):
        """Test node object argument_list for builtin func."""

        node = Node("Test", np.sum, inputs=["array"])

        assert node.signature == Signature([Parameter("array", 1)])
        assert node([1, 2]) == 3.0
        assert "Sum of array elements over a given axis." in node.doc

    def test_signature_less(self):
        """Test when a node does not have signature nor arguments defined."""

        node = Node("Test", np.add)
        assert node.signature == Signature()

    def test_model_as_function(self, mmodel_G):
        """Test ``model_func`` is used when the function input is a Model instance."""

        model = Model("model_instance", mmodel_G, BasicHandler)
        node = Node("Test", model)
        assert node(1, 4, d=2, f=3) == (27, math.log(3, 4))

        # check the model_func is used
        # the underlying function does not check inputs
        # it gives a type error due to the dictionary access
        assert node.node_func(a=1, b=4, d=2, f=3) == (27, math.log(3, 4))

        with pytest.raises(TypeError, match="missing a required argument: 'f'"):
            node.node_func(a=1, b=4, d=2)
