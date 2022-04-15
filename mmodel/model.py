from abc import ABCMeta, abstractmethod
import h5py

from mmodel.utility import (
    graph_signature,
    graph_returns,
    graph_topological_sort,
    param_counter,
    replace_signature
)
from mmodel.loop import subgraph_from_params, redirect_edges, basic_loop
from mmodel.draw import draw_graph, draw_plain_graph
from mmodel.doc import parse_description_graph, parse_description_doc


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

        self.sig_replacement = None
        self.reset_model()

    def reset_model(self):
        """Define the true signature of the graph if object replacement"""

        signature = graph_signature(self.G)

        if self.sig_replacement is not None:
            signature = replace_signature(signature, self.sig_replacement)

        self.__signature__ = signature
        self.returns = graph_returns(self.G)
        self.topological_order = graph_topological_sort(self.G)
        

    def __call__(self, *args, **kwargs):
        """Execute graph model by layer"""

        data_instance = self._initiate(*args, **kwargs)

        for node, node_attr in self.topological_order:
            try:
                self._run_node(data_instance, node, node_attr)
            except Exception as e:
                self._raise_node_exception(data_instance, node, node_attr, e)

        return self._finish(data_instance, self.returns)

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
    def _finish(self, data_instance, returns):
        """Finish execution"""

    def loop_parameter(self, parameters, method=basic_loop, *args, **kwargs):
        """Construct loop

        Loops with the same parameters are not allowed

        TODO
            restructure where the subgraph copy happens
            better loop parameter checking when duplication occurs
        """
        param_string = ", ".join(parameters)
        node_name = f"loop {param_string}"

        if node_name in self.G:
            raise Exception(f"{node_name} already exist")

        # description of the subgraph
        node_doc = f"{method.__name__} method"

        subgraph = subgraph_from_params(self.G, parameters)

        # if subgraph.
        loop_node = self._create_looped_subgraph(subgraph, parameters, method)

        node_obj, returns = loop_node

        self.G = redirect_edges(
            self.G, subgraph, node_name, node_obj, returns, parameters
        )
        self.G.nodes[node_name]["node_obj"].G.graph.update(
            {"name": node_name, "doc": node_doc}
        )
        # reset values
        self.reset_model()

    def _create_looped_subgraph(self, subgraph, params, method):
        """Turn subgraph into a loopped variable returns the node attribute"""

        node_obj = method(type(self)(subgraph), params)

        return node_obj, node_obj.returns

    def draw_graph(self, show_detail=False):
        """Draw graph"""
        if show_detail:
            label = parse_description_graph(self._long_description(False))
            return draw_graph(self.G, self.__name__, label)
        else:
            label = parse_description_graph(self._short_description())
            return draw_plain_graph(self.G, self.__name__, label)

    def _short_description(self):
        """model short documentation"""

        short_docstring = self.G.doc.partition("\n")[0]

        des_list = [
            ("name", self.__name__),
            ("doc", short_docstring),
            ("model type", self.__class__.__name__),
        ]

        return des_list

    def _long_description(self, long_docstring=True):
        """model long documentation"""
        if long_docstring:
            doc = self.G.doc
        else:
            doc = self.G.doc.partition("\n")[0]
        des_list = [
            ("name", self.__name__),
            ("doc", doc),
            ("model type", str(self.__class__)),
            ("parameters", str(self.__signature__)),
            ("returns", ", ".join(self.returns)),
        ]

        return des_list

    def __repr__(self):
        """Show instance description"""
        title = f"{self.__class__.__name__} instance\n\n"
        return title + parse_description_doc(self._long_description()).expandtabs(4)


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

        returns = node_attr["returns"]
        if len(returns) == 1:
            value_dict[returns[0]] = func_output
        else:
            value_dict.update(dict(zip(returns, func_output)))

        for key in parameters:
            count[key] -= 1
            if count[key] == 0:
                del value_dict[key]

    def _raise_node_exception(self, data_instance, node, node_attr, e):
        """Raise exception

        Delete intermediate attributes
        """

        raise Exception(f"Exception occurred for node {node, node_attr}") from e

    def _finish(self, data_obj, returns):
        """Finish and return values"""
        value_dict = data_obj[0]
        if len(returns) == 1:
            return_val = value_dict[returns[0]]
        else:
            return_val = tuple(value_dict[rt] for rt in returns)

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

        returns = node_attr["returns"]
        if len(returns) == 1:
            value_dict[returns[0]] = func_output
        else:
            value_dict.update(dict(zip(returns, func_output)))

    def _raise_node_exception(self, value_dict, node, node_attr, e):
        """Raise exception

        Delete intermediate attributes
        """

        raise Exception(f"Exception occurred for node {node, node_attr}") from e

    def _finish(self, value_dict, returns):
        """Finish and return values"""
        if len(returns) == 1:
            return_val = value_dict[returns[0]]
        else:
            return_val = tuple(value_dict[rt] for rt in returns)

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

        returns = node_attr["returns"]
        if len(returns) == 1:
            self.write({returns[0]: func_output}, exe_group)
        else:
            self.write(dict(zip(returns, func_output)), exe_group)

    def _finish(self, data_instance, returns):
        """output parameters based on returns"""

        f, exe_group = data_instance

        if len(returns) == 1:
            rt = self.read(returns[0], exe_group)
        else:
            rt = tuple(self.read(rt, exe_group) for rt in returns)

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

        return node_obj, node_obj.returns
