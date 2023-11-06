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
    parameters = dict(sig.parameters)
    old_param = list(parameters.keys())

    # check if input parameters are less than the parameters required
    # excludes parameters with defaults
    required = []
    defaults = []
    if_var_keyword = False
    for param in parameters.values():
        if (param.kind <= 1 or param.kind == 3) and param.default is Parameter.empty:
            required.append(param.name)
        elif param.default is not Parameter.empty:
            defaults.append(param.name)
        elif param.kind == 4:
            if_var_keyword = True

    # check if the inputs are enough for the function
    if len(required) > len(inputs):
        raise ValueError("Not enough inputs for the function")

    # check if the inputs are too much for the function
    if len(required) + len(defaults) < len(inputs) and not if_var_keyword:
        raise ValueError("Too many inputs for the function")

    new_param = []
    for element in inputs:
        new_param.append(Parameter(element, kind=Parameter.POSITIONAL_OR_KEYWORD))
    new_sig = Signature(new_param)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments

        adjusted_kwargs = {}
        for i, p in enumerate(inputs):
            adjusted_kwargs[old_param[i]] = arguments.pop(p)

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
        new_param.append(Parameter(element, kind=Parameter.POSITIONAL_OR_KEYWORD))

    new_sig = Signature(new_param)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments
        return func(*arguments.values())

    wrapped.__signature__ = new_sig
    return wrapped


def convert_signature(func):
    """Convert function signature to pos_or_keywords.

    The method ignores "args", and "kwargs".
    Note the signature does not include parameters with default values.
    Use inputs to include the parameters.
    """

    sig = signature(func)
    parameters = dict(sig.parameters)

    param_list = []
    for param in parameters.values():
        if (param.kind == 1 or param.kind == 3) and param.default is Parameter.empty:
            param_list.append(param)
        elif param.kind == 0:  # defaults cannot be add to pos only parameter
            param_list.append(
                Parameter(param.name, kind=Parameter.POSITIONAL_OR_KEYWORD)
            )

    new_sig = Signature(parameters=param_list)

    @wraps(func)
    def wrapped(*args, **kwargs):
        arguments = new_sig.bind(*args, **kwargs).arguments
        args, kwargs = split_arguments(sig, arguments)
        return func(*args, **kwargs)

    wrapped.__signature__ = new_sig
    return wrapped


def restructure_signature(
    signature, default_dict, kind=Parameter.POSITIONAL_OR_KEYWORD
):
    """Add defaults to signature for Model.

    Here the parameter kinds are replaced with kind (defaults
    to POSITIONAL_OR_KEYWORD), and defaults are applied.
    The final signatures are sorted. The function is used in
    the Model signature definition, therefore no VAR_POSITIONAL
    or VAR_KEYWORD should be in the signature.


    :param inspect.Signature signature: signature to add defaults
    :param dict default_dict: default values for the parameters
    :param int kind: parameter kind
    """

    param_list = []
    for param in signature.parameters.values():
        param_list.append(
            Parameter(
                param.name,
                kind=kind,
                default=default_dict.get(param.name, Parameter.empty),
            )
        )

    return Signature(sorted(param_list, key=param_sorter))


def has_signature(func):
    """Check if the function has a signature.

    The function checks if the function has a signature. If the
    function has a signature, the function returns True. If the
    function does not have a signature, the function returns False.
    """

    try:
        signature(func)
        return True
    except ValueError:
        return False


def check_signature(func):
    """Check if the function signature has parameters with default values.

    If the function has position-only, or var-positional,
    or var-keyword, or default values, the function returns False.
    """

    sig = signature(func)
    for param in sig.parameters.values():
        if (
            param.kind not in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
            or param.default is not Parameter.empty
        ):
            return False
    return True
