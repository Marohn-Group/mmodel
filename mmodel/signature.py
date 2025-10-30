from inspect import signature, Parameter, Signature
from functools import wraps
from mmodel.utility import param_sorter


def restructure_signature(signature, default_dict):
    """Add defaults to signature for Model.

    Here the parameter kinds are replaced with kind defaults
    to positional-or-keyword, and defaults are applied.
    The final signature is sorted.

    :param inspect.Signature signature: signature to add defaults to
    :param dict default_dict: default values for the parameters
    """

    param_list = []
    for param in signature.parameters.values():
        default = default_dict.get(param.name, Parameter.empty)
        param_list.append(Parameter(param.name, kind=1, default=default))

    return Signature(sorted(param_list, key=param_sorter))


def get_parameters(func):
    r"""Get the parameter list for the function.

    If the function has no signature, the function returns
    a list with \*args and \*\*kwargs.
    Empty input definition is allowed; therefore, a function
    without a signature and without argument lists is valid.

    :param callable func: function to get the parameters from
    """

    try:
        sig = signature(func)
        return list(sig.parameters.values())
    except ValueError:
        return [Parameter("args", kind=2), Parameter("kwargs", kind=4)]


def get_node_signature(base_params, inputs_list):
    """Get the node signature based on the function and argument lists.

    If the inputs_list is empty, the function returns
    the signature with only the required parameters and no var-parameters.
    If the inputs_list is not empty, the function checks if the
    argument lists meet the minimum and maximum requirements of the function.
    The inputs can be separated by "*" to indicate keyword-only parameters.

    :param list base_params: list of parameters
    :param list inputs_list: list of input parameters
    """

    if not inputs_list:
        sig_param = []
        for param in base_params:
            if param.default is Parameter.empty and param.kind != 2 and param.kind != 4:
                sig_param.append(param)

    else:
        if "*" in inputs_list:
            var_index = inputs_list.index("*")
            arglist = inputs_list[:var_index]
            kwarglist = inputs_list[var_index + 1 :]
        else:
            arglist = inputs_list
            kwarglist = []

        assert check_args(base_params, arglist)
        assert check_kwargs(base_params, kwarglist)

        # create the new signature
        sig_param = [Parameter(name, kind=1) for name in arglist] + [
            Parameter(name, kind=3) for name in kwarglist
        ]

    node_sig = Signature(sig_param)
    return node_sig


def convert_func(func, sig):
    """Wrap the input node function and redirect the input parameters.

    The signature is constructed in the node definition that defines
    the new signature following the old signature.
    The wrapper splits the arguments into positional and keyword arguments,
    and applies them to the function.
    """

    params = sig.parameters.values()
    arg_keys = [p.name for p in params if p.kind < 2]
    kwarg_keys = [p.name for p in params if p.kind > 2]

    @wraps(func)
    def wrapper(**kwargs):
        # order the dictionary first
        try:
            arg_list = [kwargs[k] for k in arg_keys]
            kwarg_dict = {k: kwargs[k] for k in kwarg_keys}
        except KeyError as e:
            # have the same behavior as a regular function
            raise TypeError(f"missing a required argument: {e}")

        return func(*arg_list, **kwarg_dict)

    wrapper.__signature__ = sig

    return wrapper


def check_signature(base_params, param_list, param_type, nonvar_kind, var_kind):
    """Check if the function signature is valid.

    Check for the number of parameters based on original
    signature requirements.
    """

    argname = []
    required = []
    var_args = False
    for param in base_params:
        if param.kind in var_kind:
            var_args = True
        elif param.kind in nonvar_kind:
            argname.append(param.name)
            if param.default is Parameter.empty:
                required.append(param.name)

    if not var_args:
        if len(param_list) > len(argname):
            raise Exception(
                f"too many {param_type} arguments, "
                f"maximum {len(argname)} but got {len(param_list)}"
            )

    if len(param_list) < len(required):
        raise Exception(
            f"not enough {param_type} arguments, "
            f"minimum {len(required)} but got {len(param_list)}"
        )

    return True


def check_kwargs(base_params, kwarglist):
    """Check if kwargs list is valid.

    :param list base_params: list of signature parameters
    :param list kwarglist: list of keyword arguments
    """

    return check_signature(base_params, kwarglist, "keyword", [3], [4])


def check_args(base_params, arglist):
    """Check if args list is valid.

    :param list base_params: list of signature parameters
    :param list arglist: list of positional arguments
    """

    return check_signature(base_params, arglist, "positional", [0, 1], [2])
