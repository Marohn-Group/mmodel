"""Test Handler classes

Currently all models inherits from TopologicalHandler, which is an abstract class.
The test strategy works as the following:

- create a mock instance of the abstract class, and test the attributes
- test individual method of child class methods
- test Handler as a whole

"""


from mmodel.handler import (
    TopologicalHandler,
    MemHandler,
    MemDict,
    PlainHandler,
    H5Handler,
)
from inspect import signature
import pytest
import h5py
import numpy as np
import math
from tests.conftest import graph_equal
import re


class TestMemDict:
    """Test the behavior of the customized dictionary"""

    @pytest.fixture
    def memdict(self):
        return MemDict({"a": 1, "b": 2, "c": 1}, {"a": "hello", "b": "world"})

    def test_key_deletion(self, memdict):
        """Test if 'a' is deleted after a single extraction"""
        memdict["a"]
        assert "a" not in memdict

        memdict["b"]
        assert "b" in memdict
        memdict["b"]
        assert "b" not in memdict

    def test_key_update(self, memdict):
        """Test update of the dictionary"""

        memdict["c"] = "hello world"
        assert memdict["c"] == "hello world"
        assert "c" not in memdict

    def test_counter_value(self, memdict):
        """Test counter value after parameters are extracted"""

        memdict["a"] = "hello world"
        assert memdict.counter["a"] == 1
        memdict["a"]
        assert memdict.counter["a"] == 0
        memdict["b"]
        assert memdict.counter["b"] == 1

    def test_deletion_during_iteration(self, memdict):
        """Test the deletion method during iteration"""

        with pytest.raises(RuntimeError, match="MemDict is not iterable"):
            for key in memdict:
                pass


class TestTopologicalHandler:
    """Test class TopologicalModel"""

    def test_TopologicalModel(self, monkeypatch, mmodel_G, mmodel_signature):
        """Test TopologicalModel

        TopologicalModel contains abstract method, therefore it cannot instantiate
        itself. Here we monkeypatch to empty the __abstractmethods__ attribute
        and test the basic init and method behaviors.
        """
        # monkeypatch the abstractmethod to empty to TopologicalModel
        # so that it can instantiate
        monkeypatch.setattr(TopologicalHandler, "__abstractmethods__", set())

        model = TopologicalHandler(mmodel_G, ["c"])

        assert signature(model) == mmodel_signature

        assert graph_equal(model.graph, mmodel_G)
        assert model.returns == ["c", "k", "m"]


@pytest.fixture(scope="module")
def node_a_attr():
    def func_a(arg1, arg2, arg3):
        """Test function node for Model _run_node method"""
        return arg1 + arg2 + arg3

    return {"func": func_a, "sig": signature(func_a), "returns": ["arg4"]}


@pytest.fixture(scope="module")
def node_b_attr():
    def func_b(arg1, arg2, arg3):
        """Test function node for Model _run_node method"""
        return arg1 + arg2, arg3

    return {"func": func_b, "sig": signature(func_b), "returns": ["arg4", "arg5"]}


class TestMemHandler:
    """Test class Model"""

    @pytest.fixture
    def handler_instance(self, mmodel_G):
        """Create Model object for the test"""
        return MemHandler(mmodel_G, [])

    def test_instance_attrs(self, handler_instance):
        """Test the memhandler count attribute"""
        count = {"a": 1, "b": 2, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1, "m": 1, "k": 1}
        assert handler_instance.counter == count

    def test_initiate(self, handler_instance):
        """Test initiate method

        The data instance should return two dictionaries
        one ordered dictionary with the correct arguments
        one dictionary with number of value counts in the graph

        The signature is a, b, f, b = 2
        b however, is not automatically filled
        """
        value_dict = handler_instance.initiate(a=1, d=2, f=5, b=2)
        # MemDict is not iterable
        assert value_dict.data == {"a": 1, "d": 2, "f": 5, "b": 2}
        assert value_dict.counter == {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 1,
            "e": 1,
            "f": 1,
            "g": 1,
            "m": 1,
            "k": 1,
        }

    def test_run_node(self, handler_instance, node_a_attr, node_b_attr):
        """Test run_node method

        Separate data instance and nodes are provided for the tests.
        The test tests if the output is correct and is correctly zipped.

        The func_a has 1 output, and the output is a numpy array.
        All input parameters have count of 1, they should be 0 after
        the execution and the value_dict should only contain "arg4"

        The func_b has 2 outputs. The "arg2" has count of 2, its value
        is perserved after the execution.
        """

        value_dict_a = {"arg1": np.arange(5), "arg2": 4.5, "arg3": 2.2}
        count_a = {"arg1": 1, "arg2": 1, "arg3": 1, "arg4": 1}
        data_instance_a = MemDict(count_a, value_dict_a)

        value_dict_b = {"arg1": 10, "arg2": 14, "arg3": 2, "arg4": 1}
        count_b = {"arg1": 1, "arg2": 2, "arg3": 1, "args4": 1}
        data_instance_b = MemDict(count_b, value_dict_b)

        handler_instance.run_node(data_instance_a, "node_a", node_a_attr)
        handler_instance.run_node(data_instance_b, "node_b", node_b_attr)

        assert list(data_instance_a.data.keys()) == ["arg4"]
        assert np.array_equal(data_instance_a["arg4"], np.arange(6.7, 11.7))
        assert data_instance_a.counter == {"arg1": 0, "arg2": 0, "arg3": 0, "arg4": 0}

        assert data_instance_b.data == {"arg2": 14, "arg4": 24, "arg5": 2}
        # no args4 are extracted therefore there is no return
        assert data_instance_b.counter == {"arg1": 0, "arg2": 1, "arg3": 0, "args4": 1}

    def test_finish_single_return(self, handler_instance):
        """Test _finish method

        The method should output the value directly if there is only
        one output parameter.
        """

        value_dict = MemDict({"arg4": 1, "arg5": 1}, {"arg4": 1, "arg5": 4.5})
        assert handler_instance.finish(value_dict, ["arg4"]) == 1

    def test_finish_multiple_return(self, handler_instance):
        """Test _finish method

        The method should return a tuple with multiple return variable
        """

        value_dict = MemDict({"arg4": 1, "arg5": 1}, {"arg4": 1, "arg5": 4.5})
        assert handler_instance.finish(value_dict, ["arg4", "arg5"]) == (1, 4.5)

    def test_raise_exception(self, handler_instance):
        """Test _raise_exception"""

        with pytest.raises(Exception):
            handler_instance.raise_node_exception(None, "node", {}, Exception("Test"))

    def test_node_exception(self, handler_instance):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            handler_instance(a=1, d="2", f=3, b=2)

    def test_execution(self, handler_instance):
        """Test running the model as a function"""

        assert handler_instance(a=10, d=15, f=20, b=2) == (-720, math.log(12, 2))
        assert handler_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))

    def test_add_returns(self, mmodel_G):
        """Test if the handler returns the proper parameters add_returns specified"""

        handler_instance = MemHandler(mmodel_G, ["c"])
        assert handler_instance(a=10, d=15, f=20, b=2) == (12, -720, math.log(12, 2))


class TestPlainHandler:
    """Test class Model"""

    @pytest.fixture
    def handler_instance(self, mmodel_G):
        """Create Model object for the test"""
        return PlainHandler(mmodel_G, [])

    def test_initiate(self, handler_instance):
        """Test _initiate method

        The signature is a, d, f, b = 2
        """
        data_instance = handler_instance.initiate(a=1, d=2, f=5, b=2)
        assert data_instance == {"a": 1, "d": 2, "f": 5, "b": 2}

    def test_run_node(self, handler_instance, node_a_attr, node_b_attr):
        """Test _run_node method

        Separate data instance and nodes are provided for the tests.
        The test tests if the output is correct and is correctly zipped.

        The func_a has 1 output, and the output is a numpy array.
        The func_b has 2 outputs.
        """

        value_dict_a = {"arg1": np.arange(5), "arg2": 4.5, "arg3": 2.2}
        value_dict_b = {"arg1": 10, "arg2": 14, "arg3": 2}

        handler_instance.run_node(value_dict_a, "node_a", node_a_attr)
        handler_instance.run_node(value_dict_b, "node_b", node_b_attr)

        assert list(value_dict_a.keys()) == ["arg1", "arg2", "arg3", "arg4"]
        assert np.array_equal(value_dict_a["arg4"], np.arange(6.7, 11.7))

        assert value_dict_b == {
            "arg1": 10,
            "arg2": 14,
            "arg3": 2,
            "arg4": 24,
            "arg5": 2,
        }

    def test_finish(self, handler_instance):
        """Test _finish method

        Finish method should output the value directly if there is only
        one output parameter. A tuple if there are multiple output parameter
        """

        value_dict = {"arg4": 1, "arg5": 4.5}
        assert handler_instance.finish(value_dict, ["arg4"]) == 1
        assert handler_instance.finish(value_dict, ["arg4", "arg5"]) == (1, 4.5)

    def test_raise_exception(self, handler_instance):
        """Test _raise_exception"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('node', {'key': 'value'}\)"
        ):
            handler_instance.raise_node_exception(
                None, "node", {"key": "value"}, Exception("Test")
            )

    def test_node_exception(self, handler_instance):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            handler_instance(a=1, d="2", f=3, b=2)

    def test_execution(self, handler_instance):
        """Test running the model as a function"""

        assert handler_instance(a=10, d=15, f=20, b=2) == (-720, math.log(12, 2))
        assert handler_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))


class TestH5Handler:
    """Test class Model"""

    @pytest.fixture
    def h5_filename(self, tmp_path):

        # "/" is basically join, tmp_path is pathlib.Path object
        # the file does not exist at this point
        # the tmpdir only saves the three most recent runs
        # there is no need to delete them
        return tmp_path / "h5model_test.h5"

    @pytest.fixture
    def handler_instance(self, mmodel_G, h5_filename):
        """Create Model object for the test

        The scope of the tmp_path is "function", the file
        object and model instance are destroyed after each test function
        """
        return H5Handler(mmodel_G, h5_filename)

    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_read_scalar(self, scalar, value, handler_instance, h5_filename):
        """Test _read method reading attr data from h5 file"""

        f = h5py.File(h5_filename, "w")
        f[scalar] = value

        assert handler_instance.read(scalar, f) == value
        f.close()

    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_read_dataset(self, dataset, value, handler_instance, h5_filename):
        """Test _read method reading dataset from h5 file"""

        f = h5py.File(h5_filename, "w")
        f[dataset] = value

        assert all(handler_instance.read(dataset, f) == value)
        f.close()

    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_write_scalar(self, scalar, value, handler_instance, h5_filename):
        """Test writing scalar data to h5 file"""

        f = h5py.File(h5_filename, "w")
        handler_instance.write({scalar: value}, f)

        assert f[scalar][()] == value
        f.close()

    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_write_dataset(self, dataset, value, handler_instance, h5_filename):
        """Test writing dataset to h5 file"""

        f = h5py.File(h5_filename, "w")
        handler_instance.write({dataset: value}, f)

        assert all(f[dataset][()] == value)
        f.close()

    def test_initiate_group_name(self, handler_instance):
        """Test if initiate method creates experiment group

        The file should have the group {id}_{name}{exp_num}
        we close the file and check if the group is saved
        """

        f, exe_group = handler_instance.initiate(a=1, d=2, f=5, b=2)
        exe_str = f"{id(handler_instance)}_1"
        assert exe_str in f
        f.close()

    def test_run_node(self, handler_instance, h5_filename, node_a_attr, node_b_attr):
        """Test _run_node method

        Separate data instance and nodes are provided for the tests.
        The test tests if the output is correct and is correctly zipped.

        The func_a has 1 output, and the output is a numpy array.
        The func_b has 2 outputs.

        There is a precision issue in the read write with h5 file.
        The test assertion is that they are close with relative tolerance of
        1e-8 and absolute tolerance of 1e-10
        """

        f = h5py.File(h5_filename, "w")
        func_a_group = f.create_group("func_a")
        func_a_group["arg1"] = np.array([1, 2, 3])
        func_a_group["arg2"] = np.array([0.1, 0.2, 0.3])
        func_a_group["arg3"] = np.array([0.01, 0.02, 0.03])

        func_b_group = f.create_group("func_b")
        func_b_group["arg1"] = 10
        func_b_group["arg2"] = 14
        func_b_group["arg3"] = 2

        handler_instance.run_node((f, func_a_group), "node_a", node_a_attr)
        handler_instance.run_node((f, func_b_group), "node_b", node_b_attr)

        assert np.allclose(
            func_a_group["arg4"][()],
            np.array([1.11, 2.22, 3.33]),
            rtol=1e-8,
            atol=1e-10,
        )
        assert func_b_group["arg4"][()] == 24
        assert func_b_group["arg5"][()] == 2

    def test_finish(self, handler_instance, h5_filename):
        """Test _finish method

        Finish method should output the value directly if there is only
        one output parameter. A tuple if there are multiple output parameter.
        The _finish method closes file at the end, therefore for testing
        a new file is opened each time.
        """

        with h5py.File(h5_filename, "w") as f:
            exe_group = f.create_group("exe_test")
            exe_group["arg4"] = 1.14
            exe_group["arg5"] = 10
            exe_group["arg6"] = np.array([1.11, 2.22, 3.33])

        f = h5py.File(h5_filename, "r")
        exe_group = f["exe_test"]
        assert handler_instance.finish((f, exe_group), ["arg4"]) == 1.14
        assert not f  # check if it still open

        f = h5py.File(h5_filename, "r")
        exe_group = f["exe_test"]
        assert handler_instance.finish((f, exe_group), ["arg4", "arg5"]) == (1.14, 10)
        assert not f  # check if it still open

        f = h5py.File(h5_filename, "r")
        exe_group = f["exe_test"]
        assert np.array_equal(
            handler_instance.finish((f, exe_group), ["arg6"]),
            np.array([1.11, 2.22, 3.33]),
        )
        assert not f  # check if it still open

    def test_raise_exception(self, handler_instance, h5_filename):
        """Test _raise_exception"""

        f = h5py.File(h5_filename, "w")
        exe_group = f.create_group("exe_test")

        with pytest.raises(Exception):
            handler_instance.raise_node_exception(
                (f, exe_group), "node", {"node_obj": None}, Exception("Test Error")
            )

        assert not f  # check if it still open

        with h5py.File(h5_filename, "r") as f:
            assert (
                f["exe_test"].attrs["note"]
                == "Exception occurred for node ('node', {'node_obj': None}): Test Error"
            )

    def test_node_exception(self, handler_instance, h5_filename):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            handler_instance(a=1, d="2", f=3, b=2)

        with h5py.File(h5_filename, "r") as f:

            assert bool(
                re.match(
                    r".+ occurred for node \('subtract', .+\)",
                    f[f"{id(handler_instance)}_1"].attrs["note"],
                )
            )

    def test_execution(self, handler_instance):
        """Test running the model as a function"""

        assert handler_instance(a=10, d=15, f=20, b=2) == (-720, math.log(12, 2))
        assert handler_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))
