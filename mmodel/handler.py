from collections import UserDict
from mmodel.utility import model_signature, graph_topological_sort, param_counter
from datetime import datetime
import h5py

ERROR_FORMAT = """\
Exception occurred for node '{node}':
--- node info ---
{node_str}
--- input info ---
{input_str}
"""


class TopologicalHandler:
    """Base class for executing graph nodes in topological order"""

    DataClass = None

    def __init__(self, graph, returns: list = [], **datacls_kwargs):

        self.__signature__ = model_signature(graph)
        self.returns = returns
        self.order = graph_topological_sort(graph)
        self.graph = graph
        self.datacls_kwargs = datacls_kwargs

    def __call__(self, **kwargs):
        """Execute graph model by layer"""

        data = self.DataClass(kwargs, **self.datacls_kwargs)

        for node, node_attr in self.order:
            self.run_node(data, node, node_attr)

        result = self.finish(data, self.returns)

        return result

    def run_node(self, data, node, node_attr):
        """Run individual node"""

        parameters = node_attr["sig"].parameters
        kwargs = {key: data[key] for key in parameters}
        try:
            # execute
            func_output = node_attr["func"](**kwargs)
            returns = node_attr["returns"]
            if len(returns) == 1:
                data[returns[0]] = func_output
            else:
                data.update(dict(zip(returns, func_output)))
        except:
            # format the error message

            try:  # if the data class need to be closed
                data.close()
            except:
                pass

            node_str = self.graph.view_node(node)
            input_str = "\n".join(
                [f"  {key} = {repr(value)}" for key, value in kwargs.items()]
            )
            msg = ERROR_FORMAT.format(node=node, input_str=input_str, node_str=node_str)
            raise Exception(msg)

    def finish(self, data, returns):
        """Finish execution"""

        if len(returns) == 1:
            result = data[returns[0]]
        else:
            result = tuple(data[rt] for rt in returns)

        try:  # if the data class need to be closed
            data.close()
        except:
            pass

        return result


class MemData(UserDict):
    """Modify dictionary that checks the counter every time a value is accessed

    The iteration method is
    """

    def __init__(self, data, counter):
        """Counter is a copy of the counter dictionary"""
        self.counter = counter.copy()
        super().__init__(data)

    def __getitem__(self, key):
        """When a key is accessed, reduce the counter

        If counter has reached the zero, pop the value (key is deleted)
        elsewise return the key.
        """

        self.counter[key] -= 1

        if self.counter[key] == 0:
            # return the value and delete the key in dictionary
            value = super().__getitem__(key)
            del self[key]
            return value

        else:
            return super().__getitem__(key)

    # def __iter__(self):
    #     """Prevent iteration that reduces the counter"""
    #     raise RuntimeError("MemDict is not iterable")


class H5Data:
    """Data class to interact with underlying h5 file

    :param str fname: h5 file name
    :param str gname: group name for the data entry

    The timestamp is appended to gname to ensure unique entry
    (in the case that the function runs really fast, a 0 is appended
    to the end of the file name.)
    """

    def __init__(self, data, fname, gname):

        self.fname = fname

        self.f = h5py.File(self.fname, "a")
        try:
            self.gname = f"{gname} {datetime.now()}"
            self.group = self.f.create_group(self.gname)
        except:
            # add a digit to time (might not be the best solution)
            self.gname += "0"
            self.group = self.f.create_group(self.gname)

        for key, value in data.items():
            self[key] = value

    def __getitem__(self, key):
        """Read dataset/attribute by group

        :param str key: value name
        :param h5py.group group: open h5py group object
        """

        return self.group[key][()]

    def __setitem__(self, key, value):
        """Write h5 dataset/attribute by group

        If the object type cannot be recognized by HDF5, the string representation
        of the object is written as attribute
        :param dict value_dict: dictionary of values to write
        :param h5py.group group: open h5py group object
        """
        try:
            self.group.create_dataset(key, data=value)
        # except ValueError:
        #     # ValueError: Unable to create dataset (name already exists)
        #     # The error should not occur since all key values are unique
        #     self.group[key] = value
        except TypeError:
            # TypeError: Object dtype dtype('O') has no native HDF5 equivalent
            self.group.attrs[key] = str(value)

    def close(self):
        """Close the data object"""
        self.f.close()


class BasicHandler(TopologicalHandler):
    """Basic handler, use dictionary as data class"""

    DataClass = dict


class MemHandler(TopologicalHandler):
    """Memory optimized handler, delete intermediate values when necessary

    The process works by keep a record of parameter counter. See MemData class
    for more details.
    """

    DataClass = MemData

    def __init__(self, graph, returns: list = []):
        """Add counter to the object"""

        counter = param_counter(graph, returns)

        super().__init__(graph, returns, counter=counter)


class H5Handler(TopologicalHandler):
    """H5 Handler, saves all calculation values to a h5 file

    Each entry of the h5 file is unique, a timestamp is added after the
    given "gname".
    """

    DataClass = H5Data

    def __init__(self, graph, returns, fname: str, gname: str = ""):
        super().__init__(graph, returns, fname=fname, gname=gname)
