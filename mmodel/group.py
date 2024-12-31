from mmodel.graph import Graph
from mmodel.model import Model
from mmodel.utility import EditMixin, ReprMixin
from mmodel.metadata import modelgroupformatter


class ModelGroup(EditMixin, ReprMixin):
    """Create a group of models.

    The ModelGroup class can create multiple models that shares the same pool
    of nodes. The class reduces redundancy in node definitions.

    If different type of models are used, the subclass should change the
    ``model_type`` class attribute.  The class are effectively unmutable.
    However, we allow the edit method for bulk model default value changes.
    """

    model_type = Model
    graph_type = Graph

    def __init__(
        self,
        name,
        node_objects=None,
        model_recipes=None,
        model_defaults=None,
        doc="",
    ):
        """Create a collection of experiments.

        The models are created at instantiation time based on the instructions
        from models.

        :param list node_objects: list of nodes objects
        :param dict model_recipes: a dictionary of model arguments
            The setting contains the grouped edges and optional experiment kwargs.
            The key of the dictionary is the model name.
        :param dict model_defaults: default model settings. They can
            be overwritten by the individual model settings provided in the
            instructions.
        :param str doc: description of the model group
            The description is stored in the __doc__ attribute for documentation.
        """

        self.name = name
        self.__doc__ = self.doc = doc

        node_objects = node_objects or []
        self._node_dict = {n.name: n for n in node_objects}
        # self.add_node_objects_from(node_objects)

        self._experiments = {}
        self._model_defaults = model_defaults or {}
        model_recipes = model_recipes or {}
        self._models = {}
        for name, model_args in model_recipes.items():
            self._models[name] = self.construct_models(name, model_args)

    def construct_models(self, name, model_args):
        """Construct a model based on the model arguments."""

        model_args = model_args.copy()

        edges = model_args.pop("grouped_edges")
        G = self.graph_type(name=f"{name}_graph")
        G.add_grouped_edges_from(edges)

        node_obj_list = []
        for node in G.nodes:
            if node not in self._node_dict:
                raise KeyError(f"node {repr(node)} not found")
            node_obj_list.append(self._node_dict[node])

        G.set_node_objects_from(node_obj_list)

        base = {"group": self.name, "name": name}
        kwargs = {**base, **self._model_defaults, **model_args}
        model_obj = self.model_type(graph=G, **kwargs)
        return model_obj

    @property
    def nodes(self):
        """Return the node dictionary."""
        return self._node_dict.copy()

    @property
    def models(self):
        """Return the models dictionary."""
        return self._models

    @property
    def model_defaults(self):
        """Return the model defaults."""
        return self._model_defaults.copy()

    def edit(self, **kwargs):
        """Create a new group model based on new global settings."""

        edit_dict = self.edit_dict
        edit_dict.update(kwargs)
        return self.__class__(**edit_dict)

    def __str__(self):
        return modelgroupformatter(self)
