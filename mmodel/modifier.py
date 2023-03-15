from functools import wraps
import inspect
from mmodel.utility import parse_input, parse_parameters


def loop_modifier(func, parameter: str):
    """Modify function to iterate one given parameter.

    :param list parameter: target parameter to loop
    """

    @wraps(func)
    def loop_wrapped(**kwargs):

        loop_values = kwargs.pop(parameter)

        try:
            # make sure the parameter input is iterable
            iter(loop_values)
        except TypeError:
            raise Exception(f"{parameter} value is not iterable")

        return [func(**kwargs, **{parameter: value}) for value in loop_values]

    return loop_wrapped


def zip_loop_modifier(func, parameters: list):
    """Modify function to iterate the parameters pairwise.

    :param list parameters: list of the parameter to loop
        only one parameter is allowed. If the string of parameters is
        provided, the parameters should be delimited by ", ".
    """

    @wraps(func)
    def loop_wrapped(**kwargs):

        loop_values = [kwargs.pop(param) for param in parameters]

        result = []
        for value in zip(*loop_values):  # unzip the values

            loop_value_dict = dict(zip(parameters, value))
            rv = func(**kwargs, **loop_value_dict)
            result.append(rv)

        return result

    return loop_wrapped


def signature_modifier(func, parameters):
    """Replace node object signature.

    :param list parameters: signature parameters to replace the original
        signature. The parameters are assumed to be "POSITIONAL_OR_KEYWORD", and no
        default values are allowed. The signature will replace the original signature
        in order.

    .. Note::

        The modifier does not work with functions that have positional-only
        input parameters; or functions do not have a signature
        (built-in and numpy.ufunc). Use pos_signature_modifier instead.

    """
    sig, param_order, defaultargs = parse_parameters(parameters)

    # if there's "kwargs" in the parameter, ignore the parameter
    old_parameters = []
    for name, param in inspect.signature(func).parameters.items():
        if param.kind < 4:
            old_parameters.append(name)

    # once unzipped to return iterators, the original variable returns none
    param_pair = list(zip(old_parameters, param_order))

    @wraps(func)
    def wrapped(**kwargs):
        # assume there are no repeated signature names that are not overlapping
        # replace a, b with b, c is not allowed in the following step
        kwargs.update(defaultargs)
        for old, new in param_pair:
            kwargs[old] = kwargs.pop(new)
        return func(**kwargs)

    wrapped.__signature__ = sig
    return wrapped


def pos_signature_modifier(func, parameters):
    """Replace node object signature with position arguments.

    For functions that do not have a signature or only allow positional only
    inputs. The modifier is specifically used to change the "signature" of the builtin
    function or numpy.ufunc.

    .. note::

        The modifier is only tested against built-in function or numpy.ufunc.
    """
    sig, param_order, defaultargs = parse_parameters(parameters)

    @wraps(func)
    def wrapped(**kwargs):
        kwargs.update(defaultargs)
        # extra the variables in order
        inputs = [kwargs[key] for key in param_order]

        return func(*inputs)

    wrapped.__signature__ = sig
    return wrapped


def signature_binding_modifier(func):
    """Add parameter binding and checking for function.

    The additional wrapper is unnecessary, but to keep a consistent
    modifier syntax. The modifier can be used on wrapped functions
    that do not have a parameter binding step (ones that only allow
    keyword arguments).

    The parse_input method binds the input args and kwargs and fills
    default values automatically. The resulting function behaves the
    same as a python function.
    """

    sig = inspect.signature(func)

    @wraps(func)
    def wrapped(*args, **kwargs):

        parsed_kwargs = parse_input(sig, *args, **kwargs)

        return func(**parsed_kwargs)

    return wrapped
