"""Test Models

Currently all models inherits from TopologicalModel, which is an abstract class.
The test stredgy works as the following:

- create a mock instance of the abstract class, and test the attributes
- test individual method of child class methods
- test Model as a whole

"""

from mmodel.model import TopologicalModel, Model, PlainModel, H5Model
from inspect import signature
import pytest
from collections import OrderedDict
import h5py
import numpy as np
import math
from tests.conftest import graphs_equal
import re


class TestTopologicalModel:
    """Test class TopologicalModel"""

    def test_TopologicalModel(self, monkeypatch, mmodel_G, mmodel_signature):
        """Test TopologicalModel

        TopologicalModel contains abstract method, therefore it cannot instantiate
        itself. Here we monkeypatch to remove the abstractmethods and test
        the basic init and method behaviors.
        """
        # monkeypatch the abstractmethod to empty to TopologicalModel can
        # instantiate
        monkeypatch.setattr(TopologicalModel, "__abstractmethods__", set())

        model = TopologicalModel(mmodel_G)

        assert signature(model) == mmodel_signature
        assert model.__name__ == "test model"
        # make sure the graph is a copy
        assert model.G != mmodel_G

        graphs_equal(model.G, mmodel_G)

    def test_create_loop(self, monkeypatch, mmodel_G):
        """Test create loops for graph"""

        monkeypatch.setattr(TopologicalModel, "__abstractmethods__", set())

        model = TopologicalModel(mmodel_G)
        model.loop_parameter(params=["f"])

        assert "loop f" in model.G
        assert model.G.adj == {
            "add": {
                "subtract": {"parameters": ["c"]},
                "log": {"parameters": ["c"]},
                "loop f": {"parameters": ["c"]},
            },
            "subtract": {"loop f": {"parameters": ["e"]}},
            "log": {},
            "loop f": {},
        }

        # test the node (unwrapped) in an instance of TopologicalModel
        assert isinstance(
            model.G.nodes["loop f"]["node_obj"].__wrapped__,
            TopologicalModel,
        )

        # add second loop
        model.loop_parameter(params=["d"])
        assert "loop d" in model.G
        assert model.G.adj == {
            "add": {
                "loop d": {"parameters": ["c"]},
                "log": {"parameters": ["c"]},
            },
            "log": {},
            "loop d": {},
        }

    def test_double_loop_fails(self, monkeypatch, mmodel_G):
        """Test when two loops are created, the name does not overlap"""

        monkeypatch.setattr(TopologicalModel, "__abstractmethods__", set())

        model = TopologicalModel(mmodel_G)
        model.loop_parameter(params=["f"])
        assert "loop f" in model.G
        with pytest.raises(Exception, match="loop f already exist"):
            model.loop_parameter(params=["f"])

@pytest.fixture(scope="module")
def node_a_attr():
    def func_a(arg1, arg2, arg3):
        """Test function node for Model _run_node method"""
        return arg1 + arg2 + arg3

    return {
        "node_obj": func_a,
        "signature": signature(func_a),
        "node_type": "callable",
        "returns": ["arg4"],
    }


@pytest.fixture(scope="module")
def node_b_attr():
    def func_b(arg1, arg2, arg3):
        """Test function node for Model _run_node method"""
        return arg1 + arg2, arg3

    return {
        "node_obj": func_b,
        "signature": signature(func_b),
        "node_type": "callable",
        "returns": ["arg4", "arg5"],
    }


class TestModel:
    """Test class Model"""

    @pytest.fixture
    def model_instance(self, mmodel_G):
        """Create Model object for the test"""
        return Model(mmodel_G)

    def test_initiate(self, model_instance):
        """Test _initiate method

        The data instance should return two dictionaries
        one ordered dictionary with the correct arguments
        one dictionary with number of value counts in the graph

        The signature is a, b, f, b = 2
        the value b should be automatically filled
        """
        value_dict, count = model_instance._initiate(1, 2, 5)
        assert value_dict == OrderedDict({"a": 1, "d": 2, "f": 5, "b": 2})
        assert count == {"a": 1, "b": 2, "c": 3, "d": 1, "e": 1, "f": 1, "g": 1}

    def test_run_node(self, model_instance, node_a_attr, node_b_attr):
        """Test _run_node method

        Separate data instance and nodes are provided for the tests.
        The test tests if the output is correct and is correctly zipped.

        The func_a has 1 output, and the output is a numpy array.
        All input parameters have count of 1, they should be 0 after
        the execution and the value_dict should only contain "arg4"

        The func_b has 2 outputs. The "arg2" has count of 2, its value
        is perserved after the execution.
        """

        value_dict_a = {"arg1": np.arange(5), "arg2": 4.5, "arg3": 2.2}
        count_a = {"arg1": 1, "arg2": 1, "arg3": 1}
        data_instance_a = (value_dict_a, count_a)

        value_dict_b = {"arg1": 10, "arg2": 14, "arg3": 2}
        count_b = {"arg1": 1, "arg2": 2, "arg3": 1}
        data_instance_b = (value_dict_b, count_b)

        model_instance._run_node(data_instance_a, "node_a", node_a_attr)
        model_instance._run_node(data_instance_b, "node_b", node_b_attr)

        assert list(value_dict_a.keys()) == ["arg4"]
        assert np.array_equal(value_dict_a["arg4"], np.arange(6.7, 11.7))
        assert count_a == {"arg1": 0, "arg2": 0, "arg3": 0}

        assert value_dict_b == {"arg2": 14, "arg4": 24, "arg5": 2}
        assert count_b == {"arg1": 0, "arg2": 1, "arg3": 0}

    def test_finish(self, model_instance):
        """Test _finish method

        Finish method should output the value directly if there is only
        one output parameter. A tuple if there are multiple output parameter
        """

        value_dict = {"arg4": 1, "arg5": 4.5}
        assert model_instance._finish((value_dict, {}), ["arg4"]) == 1
        assert model_instance._finish((value_dict, {}), ["arg4", "arg5"]) == (1, 4.5)

    def test_raise_exception(self, model_instance):
        """Test _raise_exception"""

        with pytest.raises(Exception):
            model_instance._raise_node_exception(None, "node", {}, Exception("Test"))

    def test_node_exception(self, model_instance):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            model_instance(1, "2", 3)

    def test_execution(self, model_instance):
        """Test running the model as a function"""

        assert model_instance(10, 15, 20) == (-720, math.log(12, 2))
        assert model_instance(1, 2, 3, 4) == (45, math.log(5, 4))

    def test_loop(self, model_instance):
        """Test loop

        Node the return parameter shifts
        """
        model_instance.loop_parameter(params=["f"])

        assert model_instance.returns == ["m", "k"]
        assert model_instance(1, 2, [2, 3], 4) == (math.log(5, 4), [30, 45])


class TestPlainModel:
    """Test class Model"""

    @pytest.fixture
    def plainmodel_instance(self, mmodel_G):
        """Create Model object for the test"""
        return PlainModel(mmodel_G)

    def test_initiate(self, plainmodel_instance):
        """Test _initiate method

        The signature is a, b, f, b = 2
        the value b should be automatically filled
        """
        data_instance = plainmodel_instance._initiate(1, 2, 5)
        assert data_instance == OrderedDict({"a": 1, "d": 2, "f": 5, "b": 2})

    def test_run_node(self, plainmodel_instance, node_a_attr, node_b_attr):
        """Test _run_node method

        Separate data instance and nodes are provided for the tests.
        The test tests if the output is correct and is correctly zipped.

        The func_a has 1 output, and the output is a numpy array.
        The func_b has 2 outputs.
        """

        value_dict_a = {"arg1": np.arange(5), "arg2": 4.5, "arg3": 2.2}
        value_dict_b = {"arg1": 10, "arg2": 14, "arg3": 2}

        plainmodel_instance._run_node(value_dict_a, "node_a", node_a_attr)
        plainmodel_instance._run_node(value_dict_b, "node_b", node_b_attr)

        assert list(value_dict_a.keys()) == ["arg1", "arg2", "arg3", "arg4"]
        assert np.array_equal(value_dict_a["arg4"], np.arange(6.7, 11.7))

        assert value_dict_b == {
            "arg1": 10,
            "arg2": 14,
            "arg3": 2,
            "arg4": 24,
            "arg5": 2,
        }

    def test_finish(self, plainmodel_instance):
        """Test _finish method

        Finish method should output the value directly if there is only
        one output parameter. A tuple if there are multiple output parameter
        """

        value_dict = {"arg4": 1, "arg5": 4.5}
        assert plainmodel_instance._finish(value_dict, ["arg4"]) == 1
        assert plainmodel_instance._finish(value_dict, ["arg4", "arg5"]) == (1, 4.5)

    def test_raise_exception(self, plainmodel_instance):
        """Test _raise_exception"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('node', {'key': 'value'}\)"
        ):
            plainmodel_instance._raise_node_exception(
                None, "node", {"key": "value"}, Exception("Test")
            )

    def test_node_exception(self, plainmodel_instance):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            plainmodel_instance(1, "2", 3)

    def test_execution(self, plainmodel_instance):
        """Test running the model as a function"""

        assert plainmodel_instance(10, 15, 20) == (-720, math.log(12, 2))
        assert plainmodel_instance(1, 2, 3, 4) == (45, math.log(5, 4))

    def test_loop(self, plainmodel_instance):
        """Test loop

        Node the return parameter shifts
        """
        plainmodel_instance.loop_parameter(params=["f"])

        assert plainmodel_instance.returns == ["m", "k"]
        assert plainmodel_instance(1, 2, [2, 3], 4) == (math.log(5, 4), [30, 45])


class TestH5Model:
    """Test class Model"""

    @pytest.fixture
    def h5_filename(self, tmp_path):

        # "/" is basically join, tmp_path is pathlib.Path object
        # the file does not exist at this point
        # the tmpdir only saves the three most recent runs
        # there is no need to delete them
        return tmp_path / "h5model_test.h5"

    @pytest.fixture
    def h5model_instance(self, mmodel_G, h5_filename):
        """Create Model object for the test

        The scope of the tmp_path is "function", the file
        object and model instance are destroyed after each test function
        """
        return H5Model(mmodel_G, h5_filename)

    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_read_scalar(self, scalar, value, h5model_instance, h5_filename):
        """Test _read method reading attr data from h5 file"""

        f = h5py.File(h5_filename, "w")
        f[scalar] = value

        assert h5model_instance.read(scalar, f) == value
        f.close()

    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_read_dataset(self, dataset, value, h5model_instance, h5_filename):
        """Test _read method reading dataset from h5 file"""

        f = h5py.File(h5_filename, "w")
        f[dataset] = value

        assert all(h5model_instance.read(dataset, f) == value)
        f.close()

    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_write_scalar(self, scalar, value, h5model_instance, h5_filename):
        """Test writing scalar data to h5 file"""

        f = h5py.File(h5_filename, "w")
        h5model_instance.write({scalar: value}, f)

        assert f[scalar][()] == value
        f.close()

    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_write_dataset(self, dataset, value, h5model_instance, h5_filename):
        """Test writing dataset to h5 file"""

        f = h5py.File(h5_filename, "w")
        h5model_instance.write({dataset: value}, f)

        assert all(f[dataset][()] == value)
        f.close()

    def test_initiate_exe_group(self, h5model_instance):
        """Test if _initiate method creates experiment group

        The file should have the group {id}_{name}{exp_num}
        we close the file and check if the group is saved
        """

        f, exe_group = h5model_instance._initiate(1, 2, 5)
        exe_str = f"{id(h5model_instance)} test model 1"
        assert exe_str in f
        f.close()

    def test_run_node(self, h5model_instance, h5_filename, node_a_attr, node_b_attr):
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

        h5model_instance._run_node((f, func_a_group), "node_a", node_a_attr)
        h5model_instance._run_node((f, func_b_group), "node_b", node_b_attr)

        assert np.allclose(
            func_a_group["arg4"][()],
            np.array([1.11, 2.22, 3.33]),
            rtol=1e-8,
            atol=1e-10,
        )
        assert func_b_group["arg4"][()] == 24
        assert func_b_group["arg5"][()] == 2

    def test_finish(self, h5model_instance, h5_filename):
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
        assert h5model_instance._finish((f, exe_group), ["arg4"]) == 1.14
        assert not f  # check if it still open

        f = h5py.File(h5_filename, "r")
        exe_group = f["exe_test"]
        assert h5model_instance._finish((f, exe_group), ["arg4", "arg5"]) == (1.14, 10)
        assert not f  # check if it still open

        f = h5py.File(h5_filename, "r")
        exe_group = f["exe_test"]
        assert np.array_equal(
            h5model_instance._finish((f, exe_group), ["arg6"]),
            np.array([1.11, 2.22, 3.33]),
        )
        assert not f  # check if it still open

    def test_raise_exception(self, h5model_instance, h5_filename):
        """Test _raise_exception"""

        f = h5py.File(h5_filename, "w")
        exe_group = f.create_group("exe_test")

        with pytest.raises(Exception):
            h5model_instance._raise_node_exception(
                (f, exe_group), "node", {"node_obj": None}, Exception("Test Error")
            )

        assert not f  # check if it still open

        with h5py.File(h5_filename, "r") as f:
            assert (
                f["exe_test"].attrs["note"]
                == "Exception occurred for node ('node', {'node_obj': None}): Test Error"
            )

    def test_node_exception(self, h5model_instance, h5_filename):
        """Test exception is raise when there are issue with a node execution"""

        with pytest.raises(
            Exception, match=r"Exception occurred for node \('subtract', .+\)"
        ):
            h5model_instance(1, "2", 3)

        with h5py.File(h5_filename, "r") as f:

            assert bool(
                re.match(
                    r".+ occurred for node \('subtract', .+\)",
                    f[f"{id(h5model_instance)} test model 1"].attrs["note"],
                )
            )

    def test_execution(self, h5model_instance):
        """Test running the model as a function"""

        assert h5model_instance(10, 15, 20) == (-720, math.log(12, 2))
        assert h5model_instance(1, 2, 3, 4) == (45, math.log(5, 4))

    def test_loop(self, h5model_instance):
        """Test loop

        Node the return parameter shifts
        """
        h5model_instance.loop_parameter(params=["f"])

        assert h5model_instance.returns == ["m", "k"]
        assert h5model_instance(1, 2, [2, 3], 4)[0] == math.log(5, 4)
        assert all(h5model_instance(1, 2, [2, 3], 4)[1] == [30, 45])
