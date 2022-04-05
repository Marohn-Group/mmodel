from abc import ABCMeta, abstractmethod
import h5py

from mmodel.utility import (
    graph_signature,
    graph_returns,
    graph_topological_sort,
    param_counter,
)
from mmodel.loop import subgraph_from_params, redirect_edges, basic_loop
from mmodel.draw import draw_graph, draw_plain_graph
from mmodel.doc import helper


class TopologicalModel(metaclass=ABCMeta):
    """Base class for layered execution following topological generation

    Data instance is used for the execution instead of attributes. This makes
    the pipeline cleaner and better testing. A data instance can be a dictionary,
    tuple of dictionaries, or file instance. The Data instance is discarded after
    each execution or when exception occurs.
    """

    def __init__(self, G):

        self.__name__ = f"{G.name} model"
        self.G = G.copy()  # graph is a mutable object
        self.__signature__ = G.input_params
        self.return_params = G.return_params
        self.topological_order = graph_topological_sort(G)

    def __call__(self, *args, **kwargs):
        """Execute graph model by layer"""

        data_instance = self._initiate(*args, **kwargs)

        for node, node_attr in self.topological_order:
            try:
                self._run_node(data_instance, node, node_attr)
            except Exception as e:
                self._raise_node_exception(data_instance, node, node_attr, e)

        return self._finish(data_instance, self.return_params)

    @abstractmethod
    def _initiate(self, *args, **kwargs):
        """Initiate the execution"""

    @abstractmethod
    def _run_node(self, data_instance, node, node_attr):
        """Run individual node"""

    @abstractmethod
    def _raise_node_exception(self, data_instance, node, node_attr, e):
        """Raise exception when there is a node failure"""

    @abstractmethod
    def _finish(self, data_instance, return_params):
        """Finish execution"""

    def loop_parameter(self, params, method=basic_loop, *args, **kwargs):
        """Construct loop

        TODO
            restructure where the subgraph copy happens
        """
        param_string = ", ".join(params)
        node_name = f"loop {param_string}"
        while node_name in self.G:
            node_name = "outer " + node_name
        # description of the subgraph
        node_doc = f"{method.__name__} method"

        subgraph = subgraph_from_params(self.G, params)

        # if subgraph.
        loop_node = self._create_looped_subgraph(subgraph, params, method)

        node_obj, return_params = loop_node

        self.G = redirect_edges(
            self.G, subgraph, node_name, node_obj, return_params, params
        )
        self.G.nodes[node_name]["node_obj"].G.graph.update(
            {"name": node_name, "doc": node_doc}
        )
        # reset values
        self.__signature__ = graph_signature(self.G)
        self.return_params = graph_returns(self.G)
        self.topological_order = graph_topological_sort(self.G)

    def _create_looped_subgraph(self, subgraph, params, method):
        """Turn subgraph into a loopped variable returns the node attribute"""

        node_obj = method(type(self)(subgraph), params)

        return node_obj, node_obj.return_params

    def draw_graph(self, show_detail=False):
        """Draw graph"""
        if show_detail:
            label = self.doc_long.replace("\n", "\l")
            return draw_graph(self.G, self.__name__, label)
        else:
            label = self.doc_short.replace("\n", "\l")
            return draw_plain_graph(self.G, self.__name__, label)

    @property
    def doc_short(self):
        """model short documentation"""

        short_docstring = self.G.doc.partition('\n')[0]
        doc = (
            f"{self.__name__}: {short_docstring}\n"
            f"class: {self.__class__.__name__}\n"
        )
        return doc

    @property
    def doc_long(self):
        """model long documentation"""
        short_docstring, _, long_docstring = self.G.doc.partition('\n')
        short_docstring = short_docstring.strip()
        long_docstring = long_docstring.strip()
        doc = (
            f"{self.__name__}: {short_docstring}\n"
            f"{long_docstring}\n"
            f"class: {self.__class__.__name__}\n"
            f"signature: {self.__signature__}\n"
            f"returns: {', '.join(self.return_params)}\n"
        )

        return doc

    @property
    def help(self):
        """help function"""
        helper(self)


class Model(TopologicalModel):
    """Default model of mmodel module

    Model execute the graph by layer. For parameters, a counter is used
    to track all value usage. At the end of each layer, the parameter is
    deleted if the counter reaches 0.
    """

    def __init__(self, G):
        """Add counter to the object"""
        self.counter = param_counter(G)
        super().__init__(G)

    def _initiate(self, *args, **kwargs):
        """Initiate the value dictionary"""

        values = self.__signature__.bind(*args, **kwargs)
        values.apply_defaults()
        value_dict = values.arguments
        count = self.counter.copy()

        return value_dict, count

    def _run_node(self, data_instance, node, node_attr):
        """Run node

        At end of each node calculation, the counter is updated. If counter is
        zero, the value is deleted.
        """
        value_dict, count = data_instance
        parameters = node_attr["signature"].parameters
        kwargs = {key: value_dict[key] for key in parameters}

        func_output = node_attr["node_obj"](**kwargs)

        return_params = node_attr["return_params"]
        if len(return_params) == 1:
            value_dict[return_params[0]] = func_output
        else:
            value_dict.update(dict(zip(return_params, func_output)))

        for key in parameters:
            count[key] -= 1
            if count[key] == 0:
                del value_dict[key]

    def _raise_node_exception(self, data_instance, node, node_attr, e):
        """Raise exception

        Delete intermediate attributes
        """

        raise Exception(f"Exception occurred for node {node, node_attr}") from e

    def _finish(self, data_obj, return_params):
        """Finish and return values"""
        value_dict = data_obj[0]
        if len(return_params) == 1:
            return_val = value_dict[return_params[0]]
        else:
            return_val = tuple(value_dict[rt] for rt in return_params)

        return return_val


class PlainModel(TopologicalModel):
    """A fast and barebone model

    The method simply store all intermediate values in memory. The calculation steps
    are very similar to Model.
    """

    def _initiate(self, *args, **kwargs):
        """Initiate the value dictionary"""

        values = self.__signature__.bind(*args, **kwargs)
        values.apply_defaults()
        value_dict = values.arguments
        return value_dict

    def _run_node(self, value_dict, node, node_attr):
        """Run node

        At end of each node calculation, the counter is updated. If counter is
        zero, the value is deleted.
        """

        parameters = node_attr["signature"].parameters
        kwargs = {key: value_dict[key] for key in parameters}

        func_output = node_attr["node_obj"](**kwargs)

        return_params = node_attr["return_params"]
        if len(return_params) == 1:
            value_dict[return_params[0]] = func_output
        else:
            value_dict.update(dict(zip(return_params, func_output)))

    def _raise_node_exception(self, value_dict, node, node_attr, e):
        """Raise exception

        Delete intermediate attributes
        """

        raise Exception(f"Exception occurred for node {node, node_attr}") from e

    def _finish(self, value_dict, return_params):
        """Finish and return values"""
        if len(return_params) == 1:
            return_val = value_dict[return_params[0]]
        else:
            return_val = tuple(value_dict[rt] for rt in return_params)

        return return_val


class H5Model(TopologicalModel):
    """Model that stores all data in h5 file

    Each entry of the h5 file is unique, with the instance id, instance name
    and execution number
    """

    def __init__(self, G, h5_filename):

        # check if file exist
        # write id attribute
        self.h5_filename = h5_filename
        self.exe_count = 0

        super().__init__(G)

        self.entry_prefix = f"{id(self)} {self.__name__} "

    def _initiate(self, *args, **kwargs):
        """Initate dictionary value"""
        self.exe_count += 1

        values = self.__signature__.bind(*args, **kwargs)
        values.apply_defaults()
        value_dict = values.arguments

        f = h5py.File(self.h5_filename, "a")

        exe_group_name = f"{self.entry_prefix}{self.exe_count}"
        exe_group = f.create_group(exe_group_name)

        # write input dictionary to
        self.write(value_dict, exe_group)

        return f, exe_group

    def _run_node(self, data_instance, node, node_attr):
        """Run node"""

        exe_group = data_instance[1]

        parameters = node_attr["signature"].parameters
        kwargs = {key: self.read(key, exe_group) for key in parameters}

        func_output = node_attr["node_obj"](**kwargs)

        return_params = node_attr["return_params"]
        if len(return_params) == 1:
            self.write({return_params[0]: func_output}, exe_group)
        else:
            self.write(dict(zip(return_params, func_output)), exe_group)

    def _finish(self, data_instance, return_params):
        """output parameters based on returns"""

        f, exe_group = data_instance

        if len(return_params) == 1:
            rt = self.read(return_params[0], exe_group)
        else:
            rt = tuple(self.read(rt, exe_group) for rt in return_params)

        f.close()

        return rt

    def _raise_node_exception(self, data_instance, node, node_attr, e):
        """Raise exception when exception occurred for a specific node

        The error message is written as a "_node" attribute to the current group
        """
        f, exe_group = data_instance
        msg = f"{type(e).__name__} occurred for node {node, node_attr}: {e}"
        exe_group.attrs["note"] = msg
        f.close()

        raise Exception(f"Exception occurred for node {node, node_attr}") from e

    @staticmethod
    def write(value_dict, group):
        """Write h5 dataset/attribute by group

        :param dict value_dict: dictionary of values to write
        :param h5py.group group: open h5py group object
        """

        for k, v in value_dict.items():
            group.create_dataset(k, data=v)

            # if np.isscalar(v):
            #     group.attrs[k] = v
            # else:
            #     group.create_dataset(k, data=v)

    @staticmethod
    def read(key, group):
        """Read dataset/attribute by group

        :param str key: value name
        :param h5py.group group: open h5py group object
        """

        return group[key][()]

        # try:
        #     return group[key][()]
        # except KeyError:
        #     return group.attrs[key]

    def _create_looped_subgraph(self, subgraph, params, method):
        """Turn subgraph into a loopped variable returns the node attribute"""

        node_obj = method(type(self)(subgraph, self.h5_filename), params)

        return node_obj, node_obj.return_params
