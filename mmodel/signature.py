from inspect import signature, Parameter, Signature
from functools import wraps
from mmodel.utility import param_sorter


def split_arguments(sig, arguments):
    """Split the input argument into args and kwargs based on the signature.

    The kwargs need to match the inputs completely. The function
    takes care of the position-only variable in the old function.

    :param inspect.Signature sig: signature of the original function
    :param dict arguments: keyword argument values
    """

    args = []
    for param in sig.parameters.values():
        if param.kind == 0:
            args.append(arguments.pop(param.name))

    return args, arguments


def modify_signature(func, inputs):
    """Modify function signature to custom-defined inputs.

    The inputs replace the original signature in the same
    order. The resulting function is a keyword-only function.
    The conversion ignores VAR_POSITIONAL (args). For these
    functions, create a new function instead.

    :param callable func: function to change signature
    :param list inputs: new input parameters for the function.
    """

    sig = signature(func)
    param = list(dict(sig.parameters).keys())

    new_param = []
    for element in inputs:
        new_param.append(Parameter(element, kind=1))
    new_sig = Signature(new_param)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments

        adjusted_kwargs = {}
        for i, p in enumerate(inputs):
            adjusted_kwargs[param[i]] = arguments.pop(p)

        args, kwargs = split_arguments(sig, adjusted_kwargs)
        return func(*args, **kwargs)

    wrapped.__signature__ = new_sig
    return wrapped


def add_signature(func, inputs):
    """Add signature to ufunc and builtin function.

    Numpy's ufunc and builtin type do not have signatures,
    therefore a new signature is created and the input arguments
    are mapped as positional-only values.

    :param callable func: function to change signature
    :param list inputs: new input parameters for the function.
    """

    new_param = []
    for element in inputs:
        new_param.append(Parameter(element, kind=1))

    new_sig = Signature(new_param)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments
        return func(*arguments.values())

    wrapped.__signature__ = new_sig
    return wrapped


def convert_signature(func):
    """Convert function signature to pos_or_keywords.

    The method ignores "args", and "kwargs". If additional
    kwargs are required, use modify_signature with new inputs.
    Note the function removes all the default values. To keep
    the default values, use modify_signature with new inputs.
    """

    sig = signature(func)
    parameters = dict(sig.parameters)

    param_list = []
    for param in parameters.values():
        if param.kind <= 1 or param.kind == 3:
            param_list.append(Parameter(param.name, kind=1))

    new_sig = Signature(parameters=param_list)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments
        args, kwargs = split_arguments(sig, arguments)
        return func(*args, **kwargs)

    wrapped.__signature__ = new_sig
    return wrapped


def add_defaults(signature, default_dict):
    """Add defaults to signature.

    Here the parameter kinds are replaced with POSITIONAL_OR_KEYWORD,
    and defaults are applied. Note the final signature are sorted.

    :param inspect.Signature signature: signature to add defaults
    :param dict default_dict: default values for the parameters
    """

    param_list = []
    for param in signature.parameters.values():
        param_list.append(
            Parameter(
                param.name,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=default_dict.get(param.name, Parameter.empty),
            )
        )

    return Signature(sorted(param_list, key=param_sorter))
