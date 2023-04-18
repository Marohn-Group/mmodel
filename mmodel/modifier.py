__all__ = [
    "loop_input",
    "zip_loop_inputs",
    "redefine_signature",
    "redefine_pos_signature",
    "bind_signature",
    "profile_time",
]


from functools import wraps
import inspect
from mmodel.utility import parse_input, parse_parameters


def loop_input(parameter: str):
    """Modify function to iterate one given parameter.

    :param list parameter: target parameter to loop
    """

    def loop(func):
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

    loop.metadata = f"loop_input({repr(parameter)})"
    return loop


def zip_loop_inputs(parameters: list):
    """Modify function to iterate the parameters pairwise.

    :param list parameters: list of the parameter to loop
        only one parameter is allowed. If the string of parameters is
        provided, the parameters should be delimited by ", ".
    """

    def zip_loop(func):
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

    zip_loop.metadata = f"zip_loop({repr(parameters)})"
    return zip_loop


def redefine_signature(parameters: list):
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

    def signature_modifier(func):

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

    return signature_modifier


def redefine_pos_signature(parameters: list):
    """Replace node object positional signature with keyword arguments.

    For functions that do not have a signature or only allow positional only
    inputs. The modifier is specifically used to change the "signature" of the builtin
    function or numpy.ufunc.

    .. note::

        The modifier is only tested against built-in function or numpy.ufunc.
    """

    def pos_signature_modifier(func):

        sig, param_order, defaultargs = parse_parameters(parameters)

        @wraps(func)
        def wrapped(**kwargs):
            kwargs.update(defaultargs)
            # extra the variables in order
            inputs = [kwargs[key] for key in param_order]

            return func(*inputs)

        wrapped.__signature__ = sig
        return wrapped

    return pos_signature_modifier


def bind_signature(func):
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


def format_time(dt, precision):
    """Format time in seconds to a human-readable string."""

    units = {"s": 1.0, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
    for unit, scale in units.items():
        if dt >= scale:
            return f"{dt / scale:.{precision}f} {unit}"


def profile_time(number=1, repeat=1, verbose=False, precision=2):
    """Profile the execution time of a function.

    The modifier behaves similarly to the timeit module. However,
    the modifier does not suppress garbage collection during the function
    execution, therefore, the result might be slightly different.
    """
    import timeit

    timer = timeit.default_timer

    def timeit_modifier(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            time_list = []

            for _ in range(repeat):
                t0 = timer()
                for _ in range(number):
                    result = func(*args, **kwargs)
                t1 = timer()
                time_list.append((t1 - t0) / number)

            if verbose:
                print(f"{func.__name__} - raw times: {time_list}")
            else:
                term = "loops" if number > 1 else "loop"
                min_time = format_time(min(time_list), precision)
                print(
                    f"{func.__name__} - {number} {term}, "
                    f"best of {repeat}: {min_time} per loop"
                )
            return result

        return wrapped

    timeit_modifier.metadata = (
        f"profile_time(number={number}, repeat={repeat}, verbose={verbose})"
    )
    return timeit_modifier
