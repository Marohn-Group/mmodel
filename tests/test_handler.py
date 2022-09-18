"""Test Handler classes

Currently all models inherits from TopologicalHandler, which is an abstract class.
The test strategy works as the following:

- create a mock instance of the abstract class, and test the attributes
- test individual method of child class methods
- test Handler as a whole

"""


from mmodel.handler import MemData, H5Data, MemHandler, BasicHandler, H5Handler
import pytest
import math
import h5py
import numpy as np
import re

class TestMemData:
    """Test MemData class"""

    @pytest.fixture
    def data(self):
        """Create data instance"""
        return MemData({"a": "hello", "b": "world"}, counter={"a": 1, "b": 2, "c": 1})

    def test_key_deletion(self, data):
        """Test if 'a' is deleted after a single extraction"""
        data["a"]
        assert "a" not in data

        data["b"]
        assert "b" in data
        data["b"]
        assert "b" not in data

    def test_key_update(self, data):
        """Test update of the dictionary"""

        data["c"] = "hello world"
        assert data["c"] == "hello world"

    def test_counter_value(self, data):
        """Test counter value after parameters are extracted"""

        data["a"] = "hello world"
        assert data.counter["a"] == 1
        data["a"]
        assert data.counter["a"] == 0
        data["b"]
        assert data.counter["b"] == 1

    def test_counter_copy(self):
        """Test that the counter is a copy"""

        counter = {"a": 1, "b": 2, "c": 1}

        data = MemData({"a": "hello", "b": "world"}, counter=counter)
        assert data.counter is not counter  # not the same object

        # data.counter['a'] = 2
        # assert counter['a'] == 1


class Test_H5Data:
    """Test H5Data class"""

    @pytest.fixture
    def h5_filename(self, tmp_path):

        # "/" is basically join, tmp_path is pathlib.Path object
        # the file does not exist at this point
        # the tmpdir only saves the three most recent runs
        # there is no need to delete them
        return tmp_path / "h5model_test.h5"

    @pytest.fixture
    def data(self, h5_filename):
        """Create H5Data instance
        
        yield so the file is closed afterwards
        """
        data = H5Data({"a": "hello", "b": "world"}, fname=h5_filename, gname="test")
        yield data
        data.f.close()

    def test_gname(self, data):
        """Test the group name"""

        assert re.match(r"test \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}$", data.gname)


    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_write_scalar(self, scalar, value, data, h5_filename):
        """Test writing scalar data to h5 file"""

        f = h5py.File(h5_filename)
        data[scalar] = value
        assert f[data.gname][scalar][()] == value


    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_write_dataset(self, dataset, value, data, h5_filename):
        """Test writing dataset to h5 file"""
        
        f = h5py.File(h5_filename)
        data[dataset] = value
        assert all(f[data.gname][dataset][()] == value)


    def test_write_object(self, data, h5_filename):
        """Test writing unsupported object is written as attributes"""

        def func(a, b):
            return a + b
        
        f = h5py.File(h5_filename)
        data["object"] = func
        assert f[data.gname].attrs["object"] == str(func)


    @pytest.mark.parametrize("scalar, value", [("float", 1.14), ("str", b"test")])
    def test_read_scalar(self, scalar, value, data, h5_filename):
        """Test _read method reading attr data from h5 file"""

        f = h5py.File(h5_filename)
        f[data.gname][scalar] = value

        assert data[scalar] == value

    @pytest.mark.parametrize(
        "dataset, value",
        [("list", [1.11, 2.22, 3.33]), ("array", np.array([1.11, 2.22, 3.33]))],
    )
    def test_read_dataset(self, dataset, value, data, h5_filename):
        """Test _read method reading dataset from h5 file"""

        f = h5py.File(h5_filename)
        f[data.gname][dataset] = value

        assert all(data[dataset] == value)
    
    def test_close(self, data):
        """Test that the h5 file is closed"""

        data.close()

        # not sure if there is another way to check this
        assert str(data.f) == "<Closed HDF5 file>"






# def test_initiate_group_name(self, handler_instance):
#     """Test if initiate method creates experiment group

#     The file should have the group {id}_{name}{exp_num}
#     we close the file and check if the group is saved
#     """

#     # f, exe_group = handler_instance.initiate(a=1, d=2, f=5, b=2)
#     # exe_str = f"{id(handler_instance)}_1"
#     # assert exe_str in f
#     # f.close()

#     data = handler_instance.initiate(a=1, d=2, f=5, b=2)
#     exe_str = f"1_{id(data)}"
#     assert exe_str in data._f

# def test_run_node(self, handler_instance, h5_filename, node_a_attr, node_b_attr):
#     """Test _run_node method

#     Separate data instance and nodes are provided for the tests.
#     The test tests if the output is correct and is correctly zipped.

#     The func_a has 1 output, and the output is a numpy array.
#     The func_b has 2 outputs.

#     There is a precision issue in the read write with h5 file.
#     The test assertion is that they are close with relative tolerance of
#     1e-8 and absolute tolerance of 1e-10
#     """

#     f = h5py.File(h5_filename, "w")
#     func_a_group = f.create_group("func_a")
#     func_a_group["arg1"] = np.array([1, 2, 3])
#     func_a_group["arg2"] = np.array([0.1, 0.2, 0.3])
#     func_a_group["arg3"] = np.array([0.01, 0.02, 0.03])

#     func_b_group = f.create_group("func_b")
#     func_b_group["arg1"] = 10
#     func_b_group["arg2"] = 14
#     func_b_group["arg3"] = 2

#     handler_instance.run_node((f, func_a_group), "node_a", node_a_attr)
#     handler_instance.run_node((f, func_b_group), "node_b", node_b_attr)

#     assert np.allclose(
#         func_a_group["arg4"][()],
#         np.array([1.11, 2.22, 3.33]),
#         rtol=1e-8,
#         atol=1e-10,
#     )
#     assert func_b_group["arg4"][()] == 24
#     assert func_b_group["arg5"][()] == 2

# def test_finish(self, handler_instance, h5_filename):
#     """Test _finish method

#     Finish method should output the value directly if there is only
#     one output parameter. A tuple if there are multiple output parameter.
#     The _finish method closes file at the end, therefore for testing
#     a new file is opened each time.
#     """

#     with h5py.File(h5_filename, "w") as f:
#         exe_group = f.create_group("exe_test")
#         exe_group["arg4"] = 1.14
#         exe_group["arg5"] = 10
#         exe_group["arg6"] = np.array([1.11, 2.22, 3.33])

#     f = h5py.File(h5_filename, "r")
#     exe_group = f["exe_test"]
#     assert handler_instance.finish((f, exe_group), ["arg4"]) == 1.14
#     assert not f  # check if it still open

#     f = h5py.File(h5_filename, "r")
#     exe_group = f["exe_test"]
#     assert handler_instance.finish((f, exe_group), ["arg4", "arg5"]) == (1.14, 10)
#     assert not f  # check if it still open

#     f = h5py.File(h5_filename, "r")
#     exe_group = f["exe_test"]
#     assert np.array_equal(
#         handler_instance.finish((f, exe_group), ["arg6"]),
#         np.array([1.11, 2.22, 3.33]),
#     )
#     assert not f  # check if it still open

# def test_raise_exception(self, handler_instance, h5_filename):
#     """Test _raise_exception"""

#     f = h5py.File(h5_filename, "w")
#     exe_group = f.create_group("exe_test")

#     with pytest.raises(Exception):
#         handler_instance.raise_node_exception(
#             (f, exe_group), "node", {"node_obj": None}, Exception("Test Error")
#         )

#     assert not f  # check if it still open

#     with h5py.File(h5_filename, "r") as f:
#         assert (
#             f["exe_test"].attrs["note"]
#             == "Exception occurred for node ('node', {'node_obj': None}): Test Error"
#         )

# def test_node_exception(self, handler_instance, h5_filename):
#     """Test exception is raise when there are issue with a node execution"""

#     with pytest.raises(
#         Exception, match=r"Exception occurred for node \('subtract', .+\)"
#     ):
#         handler_instance(a=1, d="2", f=3, b=2)

#     with h5py.File(h5_filename, "r") as f:

#         assert bool(
#             re.match(
#                 r".+ occurred for node \('subtract', .+\)",
#                 f[f"{id(handler_instance)}_1"].attrs["note"],
#             )
#         )

# def test_execution(self, handler_instance):
#     """Test running the model as a function"""
#     import time

#     assert handler_instance(a=10, d=15, f=20, b=2) == (-720, math.log(12, 2))
#     time.sleep(0.0005)
#     assert handler_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))


exception_pattern = """\
Exception occurred for node 'log':
--- node info ---
log node
  callable: logarithm\\(c, b\\)
  returns: m
  modifiers: \\[\\]
--- input info ---
  c = 0
  b = 2"""


class HandlerTester:
    def test_execution(self, handler_instance):
        """Test running the model as a function"""

        assert handler_instance(a=10, d=15, f=20, b=2) == (-720, math.log(12, 2))
        assert handler_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))

    def test_node_exception(self, handler_instance):
        """Test when node exception a custom exception is outputted"""

        with pytest.raises(Exception, match=exception_pattern):
            handler_instance(a=-2, d=15, f=20, b=2)

    def test_intermediate_returns(self, handler_instance_mod):
        """Test if the handler returns the intermediate values

        The returned value should be a scalar not a tuple
        """

        assert handler_instance_mod(a=10, d=15, f=20, b=2) == 12


class TestBasicHandler(HandlerTester):
    """Test class Model"""

    @pytest.fixture
    def handler_instance(self, mmodel_G):
        """Create handler instance for the test"""
        return BasicHandler(mmodel_G, ["k", "m"])

    @pytest.fixture
    def handler_instance_mod(self, mmodel_G):
        """Create handler instance for the test with the intermediate value for returns"""
        return BasicHandler(mmodel_G, ["c"])


class TestMemHandler(HandlerTester):
    """Test class Model"""

    @pytest.fixture
    def handler_instance(self, mmodel_G):
        """Create Model object for the test"""
        return MemHandler(mmodel_G, ["k", "m"])

    @pytest.fixture
    def handler_instance_mod(self, mmodel_G):
        """Create handler instance for the test with the intermediate value for returns"""
        return MemHandler(mmodel_G, ["c"])


class TestH5Handler(HandlerTester):
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
        return H5Handler(mmodel_G, ["k", "m"], fname=h5_filename, gname="test run")

    @pytest.fixture
    def handler_instance_mod(self, mmodel_G, h5_filename):
        """Create handler instance for the test with the intermediate value for returns"""
        return H5Handler(mmodel_G, ["c"], fname=h5_filename, gname="test run")
