"""Modifiers are wrappers for function.
The modifiers should correctly assign updated signature
"""

from functools import wraps
import inspect
from mmodel.utility import parse_input


def loop_modifier(parameter: str):
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

    wrapper.info = f"loop_modifier({parameter})"

    return wrapper


def zip_loop_modifier(parameters):
    """Pairwise wrapper, iterates the values from loop

    :param list or string parameters: list of the parameter to loop
        only one parameter is allowed. If string of parameters are
        provided, the parameters should be delimited by ", ".
    """

    if isinstance(parameters, str):
        parameters = parameters.split(", ")

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

    wrapper.info = f"zip_loop_modifier({', '.join(parameters)})"
    return wrapper


def signature_modifier(signature_parameters):
    """Replace node object signature

    :param list signature_parameters: signature parameters to replace the original
        signature. The parameters are assumed to be "POSITIONAL_OR_KEYWORD" and no
        default values are allowed. The signature will replace the original signature
        in order.

    .. Note::
        The wrapper does not work with functions that have positional only
        input parameters. When the signature_parameter length is smaller than the
        list of original signatures, there are two cases:
        1. The additional parameters have default value - they do not show up
        in the signature, but the default values are applied to function
        2. The additional parameters do not have default value - error is thrown
        for missing input
        Currently we allow the first case senerio so no checking is performed.

    """
    sig = inspect.Signature([inspect.Parameter(var, 1) for var in signature_parameters])

    def wrapper(func):

        old_parameters = list(inspect.signature(func).parameters.keys())

        if len(signature_parameters) > len(old_parameters):
            raise Exception(
                "The number of signature modifier parameters "
                "exceeds that of function's parameters"
            )

        # once unzipped to return iterators, the original variable returns none
        param_pair = list(zip(old_parameters, signature_parameters))

        @wraps(func)
        def wrapped(**kwargs):
            # replace keys
            replace_kwargs = {old: kwargs[new] for old, new in param_pair}
            return func(**replace_kwargs)

        wrapped.__signature__ = sig

        return wrapped

    wrapper.info = f"signature_modifier{sig}"
    return wrapper


def signature_binding_modifier():
    """Add parameter binding and checking for function

    The additional wrapper is unnecessary, but to keep a consistent
    modifier syntax. The modifier can be used on wrapped functions
    that do not have a parameter binding steps (ones that only allow
    keyword arguments).

    The parse_input method, binds the input args and kwargs, and fills
    default values automatically. The resulting function behaves the
    same as a python function.
    """

    def wrapper(func):

        sig = inspect.signature(func)

        @wraps(func)
        def wrapped(*args, **kwargs):

            parsed_kwargs = parse_input(sig, *args, **kwargs)

            return func(**parsed_kwargs)

        return wrapped

    wrapper.info = "signature_binding_modifier"
    return wrapper
