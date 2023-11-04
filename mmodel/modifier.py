from functools import wraps
from inspect import signature, Parameter, Signature


def loop_input(parameter: str):
    """Modify function to iterate one given parameter.

    :param list parameter: target parameter to loop
        The target parameter name is changed to f"{param}_iter"
    """

    def loop(func):
        param_list = []
        for param in signature(func).parameters.values():
            if param.name == parameter:
                param_list.append(Parameter(f"{param}_loop", kind=1))
            else:
                param_list.append(param)

        new_sig = Signature(param_list)

        @wraps(func)
        def loop_wrapped(*args, **kwargs):
            arguments = new_sig.bind(*args, **kwargs).arguments
            loop_values = arguments.pop(f"{parameter}_loop")

            return [func(**arguments, **{parameter: value}) for value in loop_values]

        loop_wrapped.__signature__ = new_sig
        return loop_wrapped

    loop.metadata = f"loop_input({repr(parameter)})"
    return loop


def zip_loop_inputs(parameters: list):
    """Modify function to iterate the parameters pairwise.

    :param list parameters: list of the parameters to loop
        only one parameter is allowed. If the string of parameters is
        provided, the parameters should be delimited by ", ".
    """

    def zip_loop(func):
        sig = signature(func)

        @wraps(func)
        def loop_wrapped(*args, **kwargs):
            arguments = sig.bind(*args, **kwargs).arguments
            loop_values = [arguments.pop(param) for param in parameters]

            result = []
            for value in zip(*loop_values):  # unzip the values
                loop_value_dict = dict(zip(parameters, value))
                rv = func(**arguments, **loop_value_dict)
                result.append(rv)

            return result

        return loop_wrapped

    zip_loop.metadata = f"zip_loop({repr(parameters)})"
    return zip_loop


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
