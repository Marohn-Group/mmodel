import inspect
from mmodel.utility import parse_input

class Model:

    """Create the final executor"""

    def __init__(self, model_graph, handler, handler_args={}, modifiers=[]):

        self.__name__ = f"{model_graph.name} model"
        self.model_graph = model_graph.copy()

        executor = handler(model_graph, **handler_args)

        for mdf in modifiers:
            executor = mdf(executor)

        self.__signature__ = executor.__signature__
        self.returns = executor.returns
        self.executor = executor

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
                f"handler - {type(self.executor).__name__}",
                f"{self.model_graph.graph.get('doc', '')}",
            ]
        )
