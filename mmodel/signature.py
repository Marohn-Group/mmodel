from inspect import signature, Parameter, Signature
from functools import wraps
from mmodel.utility import param_sorter


def restructure_signature(signature, default_dict):
    """Add defaults to signature for Model.

    Here the parameter kinds are replaced with kind (defaults
    to positional-or-keyword), and defaults are applied.
    The final signatures are sorted.

    :param inspect.Signature signature: signature to add defaults
    :param dict default_dict: default values for the parameters
    """

    param_list = []
    for param in signature.parameters.values():
        default = default_dict.get(param.name, Parameter.empty)
        param_list.append(Parameter(param.name, kind=1, default=default))

    return Signature(sorted(param_list, key=param_sorter))


def get_parameters(func):
    r"""Get the parameter dictionary for the function.

    If the function has no signature, the function returns
    a dictionary with \*args and \*\*kwargs.
    Empty input definition is allowed, therefore a function
    without a signature and without argument lists is valid.

    :param callable func: function to get the parameters
    """

    try:
        sig = signature(func)
        return list(sig.parameters.values())
    except ValueError:
        return [Parameter("args", kind=2), Parameter("kwargs", kind=4)]


def get_node_signature(param_list, arglist, kwarglist):
    """Get the node signature based on the function and argument lists.

    If the arglist and kwarglist are empty, the function returns
    the signature with only the required parameters and no var- parameters.
    If the arglist and kwarglist are not empty, the function checks if the
    argument lists meet the minimum and maximum requirements of the function.

    :param dict param_dict: dictionary of parameters
    :param list arglist: list of positional arguments
    :param list kwarglist: list of keyword arguments
    """

    if not arglist + kwarglist:
        sig_param = []
        for param in param_list:
            if param.default is Parameter.empty and param.kind != 2 and param.kind != 4:
                sig_param.append(param)

    else:
        assert check_args(param_list, arglist)
        assert check_kwargs(param_list, kwarglist)

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
    The wrapper split the into the positional and keyword arguments,
    and apply them to the function.
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


def check_kwargs(param_list, kwarglist):
    """Check if kwargs list is valid.

    :param list kwsig: list of signature parameters
    :param list kwarglist: list of keyword arguments
    """

    kwname = []
    required = []
    var_kw = False
    for param in param_list:
        if param.kind == 4:
            var_kw = True
        elif param.kind == 3:
            kwname.append(param.name)
            if param.default is Parameter.empty:
                required.append(param.name)

    if not var_kw:
        # check if the name match
        diff = set(kwarglist) - (set(kwarglist) & set(kwname))
        if diff:
            raise Exception(f"invalid keyword argument(s): {', '.join(diff)}")

    required_diff = set(required) - set(kwarglist)
    if required_diff:
        raise Exception(
            f"missing required keyword argument(s): {', '.join(required_diff)}"
        )

    return True


def check_args(param_list, arglist):
    """Check if args list i valid.

    :param list argsig: list of signature parameters
    :param list arglist: list of positional arguments
    """

    argname = []
    required = []
    var_args = False
    for param in param_list:
        if param.kind == 2:
            var_args = True
        elif param.kind < 2:
            argname.append(param.name)
            if param.default is Parameter.empty:
                required.append(param.name)

    if not var_args:
        if len(arglist) > len(argname):
            raise Exception(
                f"too many positional arguments, "
                f"maximum {len(argname)} but got {len(arglist)}"
            )

    if len(arglist) < len(required):
        raise Exception(
            f"not enough positional arguments, "
            f"minimum {len(required)} but got {len(arglist)}"
        )

    return True
