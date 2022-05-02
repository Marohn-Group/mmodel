import inspect
from mmodel.utility import parse_input


class Model:
    """Create the final executor
    
    :param object model_graph: ModelGraph instance
    :param class handler: Handler class that handles model execution
    :param dict handler_args: additional handler argument that is not model_graph
        and add_returns. Optional, default to a empty dict.
    :param list modifiers: modifiers used for the whole graph model executable.
        Optional, defaults to a empty list.
    :param list add_returns: additional parameters to return. The parameter is
        used for retriving intermediate values of the graph model.
        Optional, defaults to a empty list.
    """

    def __init__(
        self, model_graph, handler, handler_args={}, modifiers=[], add_returns=[]
    ):

        self.__name__ = f"{model_graph.name} model"
        self.model_graph = model_graph.copy()

        executor = handler(model_graph, add_returns, **handler_args)

        for mdf in modifiers:
            executor = mdf(executor)

        self.__signature__ = executor.__signature__
        self.returns = executor.returns
        self.executor = executor

        self.handler_name = handler.__name__

    def __call__(self, *args, **kwargs):

        # process input
        data_input = parse_input(self.__signature__, *args, **kwargs)

        return self.executor(**data_input)

    def __str__(self):
        """Output callable information"""

        sig_list = [str(param) for param in self.__signature__.parameters.values()]

        return "\n".join(
            [
                f"{self.__name__}",
                f"signature - {', '.join(sig_list)}",
                f"returns - {', '.join(self.returns)}",
                f"handler - {self.handler_name}",
                f"{self.model_graph.graph.get('doc', '')}",
            ]
        )
