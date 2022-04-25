
class ModelExectuor:

    """Create the final executor"""

    def __init__(self, model_graph, modifiers, handler, handler_args=()):

        self.__name__ = f"{model_graph.name} executor"
        self.model_graph = model_graph

        executor = handler(model_graph, **handler_args)

        for mdf in modifiers:
            executor = mdf(executor)

        self.__signature__ == executor.__signature__
        self.executor = executor

    def __call__(self, *args, **kwargs):

        # process input
        data_input = self.parse_input(*args, **kwargs)

        return self.executor(**data_input)

    def parse_input(self, *args, **kwargs):
        """parse argument based on signature and input"""

        values = self.__signature__.bind(*args, **kwargs)
        values.apply_defaults()
        return values.arguments
