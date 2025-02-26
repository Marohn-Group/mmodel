from collections import UserDict
from mmodel.utility import graph_topological_sort, param_counter, modelgraph_signature
from datetime import datetime
import string
import random
from textwrap import dedent
import sys


class TopologicalHandler:
    """Base class for executing graph nodes in topological order.

    "Returns" specifies the output order. If there is only one return
    the value is outputted, otherwise a tuple is outputted. This
    behavior is similar to the Python function.

    The topological handler assumes each node has exactly one output.

    :param str name: name of the handler (same as the model instance)
    :param networkx.digraph graph: graph
    :param list returns: handler returns order
        The list should have the same or more elements than the graph returns.
        See Model constructor definition.
    """

    DataClass: type = callable

    def __init__(self, graph, returns: list, **datacls_kwargs):
        self.__signature__ = modelgraph_signature(graph)
        self.returns = returns
        self.order = graph_topological_sort(graph)
        self.graph = graph
        self.datacls_kwargs = datacls_kwargs

    def __call__(self, **kwargs):
        """Execute graph model by layer.
        The data object is not stored as an attribute to avoid repeated
        use and reduce memory usage.
        """

        data = self.DataClass(kwargs, **self.datacls_kwargs)

        for node, node_attr in self.order:
            self.run_node(data, node, node_attr)

        result = self.finish(data, self.returns)

        return result

    def node_exception(self, data, node_data, node, node_attr):
        """Exception handler for individual nodes.

        Overwrite this function for different exception formatting.
        """

        exception_format = dedent(
            """\
        An exception occurred when executing node '{node}':
        --- exception info ---
        {exc_str}
        --- node info ---
        {node_str}
        --- input info ---
        {input_str}
        """
        )
        node_object = node_attr["node_object"]
        # format the error message
        input_str = "\n".join(
            [f"{key} = {repr(value)}" for key, value in node_data.items()]
        )
        exc_type, exc_value, _ = sys.exc_info()
        exc_str = f"{exc_type.__name__}: {exc_value}"
        msg = exception_format.format(
            node=node, exc_str=exc_str, node_str=str(node_object), input_str=input_str
        )
        raise Exception(msg)

    def run_node(self, data, node, node_attr):
        """Run the individual node."""

        kwargs = {key: data[key] for key in node_attr["signature"].parameters}
        node_object = node_attr["node_object"]

        try:
            # execute
            func_result = node_object.node_func(**kwargs)
            output = node_attr["output"]
            if output:  # skip the None
                data[output] = func_result

        except:  # exception occurred while running the node
            if hasattr(data, "close"):
                data.close()

            self.node_exception(data, kwargs, node, node_attr)

    def finish(self, data, returns):
        """Finish execution."""

        if len(returns) == 0:
            result = None
        elif len(returns) == 1:
            result = data[returns[0]]
        else:
            result = tuple(data[rt] for rt in returns)

        # if the data class needs to be closed
        if hasattr(data, "close"):
            data.close()

        return result


class MemData(UserDict):
    """Modified dictionary that checks the counter every time a value is accessed."""

    def __init__(self, data, counter):
        """Counter is a copy of the counter dictionary."""
        self.counter = counter.copy()
        super().__init__(data)

    def __getitem__(self, key):
        """When a key is accessed, reduce the counter.

        If the counter has reached zero, pop the value (key is deleted)
        else wise return the key.
        """

        self.counter[key] -= 1

        if self.counter[key] == 0:
            # return the value and delete the key in the dictionary
            value = super().__getitem__(key)
            del self[key]
            return value

        else:
            return super().__getitem__(key)


class H5Data:
    """Data class to interact with underlying h5 file.

    The "timestamp-uuid" is used to ensure unique entries to the H5 group.
    The randomly generated short uuid has 36^5, which is roughly 2e9
    possibilities (picoseconds range).
    """

    def __init__(self, data, fname, gname):
        import h5py  # lazy import

        self.fname = fname

        self.f = h5py.File(self.fname, "a")

        alphabet = string.ascii_lowercase + string.digits
        shortuuid = "".join(random.choices(alphabet, k=6))
        self.gname = f"{gname} {datetime.now().strftime('%y%m%d-%H%M%S')}-{shortuuid}"
        self.group = self.f.create_group(self.gname)
        self.update(data)

    def update(self, data):
        """Write key values in bulk."""
        for key, value in data.items():
            self[key] = value

    def __getitem__(self, key):
        """Read dataset/attribute by the group.

        :param str key: value name
        :param h5py.group group: open h5py group object
        """

        return self.group[key][()]

    def __setitem__(self, key, value):
        """Write h5 dataset/attribute by the group.

        If the object type cannot be recognized by HDF5, the string representation
        of the object is written as an attribute
        :param dict value_dict: the dictionary of values to write
        :param h5py.group group: open h5py group object
        """
        try:
            self.group.create_dataset(key, data=value)
        except TypeError:
            # TypeError: Object dtype dtype('O') has no native HDF5 equivalent
            self.group.attrs[key] = str(value)

    def close(self):
        """Close the data object."""
        self.f.close()


class BasicHandler(TopologicalHandler):
    """Basic handler, use the dictionary as a data class."""

    DataClass = dict


class MemHandler(TopologicalHandler):
    """Memory optimized handler, delete intermediate values when necessary.

    The process works by keeping a record of the parameter counter.
    See MemData class for more details.
    """

    DataClass = MemData

    def __init__(self, graph, returns: list):
        """Add counter to the object."""

        counter = param_counter(graph, returns)
        super().__init__(graph, returns, counter=counter)


class H5Handler(TopologicalHandler):
    """H5 Handler, saves all calculation values to an h5 file.

    :param str fname: h5 file name
    :param str gname: group name for the data entry
    """

    DataClass = H5Data

    def __init__(self, graph, returns, fname: str, gname: str = ""):
        super().__init__(graph, returns, fname=fname, gname=gname)
