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
from textwrap import dedent


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

        assert re.match(
            r"test \d{2}\d{2}\d{2}-\d{2}\d{2}\d{2}-[a-z0-9]{6}$", data.gname
        )

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


class HandlerTester:
    def test_execution(self, handler_instance):
        """Test running the model as a function"""

        assert handler_instance(a=10, d=15, f=0, b=2) == (-3, math.log(12, 2))
        assert handler_instance(a=1, d=2, f=1, b=4) == (15, math.log(5, 4))

    def test_node_exception(self, handler_instance):
        """Test when node exception a custom exception is outputted"""

        exception_pattern = """\
        Exception occurred for node 'log':
        --- node info ---
        log
          callable: logarithm\\(c, b\\)
          return: m
          modifiers: \\[\\]
        --- input info ---
        c = 0
        b = 2"""

        with pytest.raises(Exception, match=dedent(exception_pattern)):
            handler_instance(a=-2, d=15, f=1, b=2)

    def test_intermediate_returns(self, handler_instance_mod):
        """Test if the handler returns the intermediate values

        The returned value should be a scalar not a tuple
        """

        assert handler_instance_mod(a=10, d=15, f=1, b=2) == 12


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
    """Test class Model

    In test_execution, two models are run consecutively, which tests the uniqueness of the
    h5 group entry.
    """

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
