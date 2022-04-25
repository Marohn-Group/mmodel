"""Modifiers are wrappers for function.
The modifiers should correctly assign updated signature
"""

from functools import wraps
# import inspect
# from mmodel.utility import loop_signature

def basic_loop(parameter):
    """Basic loop wrapper, iterates the values from loop

    :param list parameter: target parameter to loop
    """

    def wrapper(func):

        @wraps(func)
        def loop_wrapped(**kwargs):

            loop_values = kwargs.pop(parameter)
            return [func(**kwargs, **{parameter: value}) for value in loop_values]

        # signature = inspect.signature(func)
        # loop_sig = loop_signature(signature, [parameter])
        # loop_wrapped.__signature__ = loop_sig
    
        return loop_wrapped
    return wrapper


def zip_loop(parameters):
    """Pairwise wrapper, iterates the values from loop

    :param list parameters: list of the parameter to loop
        only one parameter is allowed
    """

    def wrapper(func):

        @wraps(func)
        def loop_wrapped(**kwargs):
            
            loop_values = [kwargs.pop(param) for param in parameters]

            result = []
            for value in zip(*loop_values):  # unzip the values

                loop_value_dict = dict(zip(parameters, value))
                rv = func(**kwargs, **loop_value_dict)
                result.append(rv)

            return result

        # signature = inspect.signature(func)
        # loop_sig = loop_signature(signature, parameters)
        # loop_wrapped.__signature__ = loop_sig
    
        return loop_wrapped
    return wrapper
