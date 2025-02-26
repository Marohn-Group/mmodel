from functools import wraps
from inspect import signature, Parameter, Signature
from types import MappingProxyType
from string import Formatter


def format_parameters(*args, **kwargs) -> list:
    """Format the parameters for stdout."""
    param_str = []
    for param in args:
        param_str.append(repr(param))
    for key, value in kwargs.items():
        param_str.append(f"{key}={repr(value)}")

    return param_str


def add_modifier_metadata(name, *args, **kwargs):
    """Decorator to add metadata to a function."""

    def decorator(func):
        param_str = format_parameters(*args, **kwargs)
        func.metadata = f"{name}({', '.join(param_str)})"
        func.args = tuple(args)
        func.kwargs = MappingProxyType(kwargs)
        func.ismodifier = True

        return func

    return decorator


def loop_input(parameter: str):
    """Modify function to iterate one given parameter.

    :param list parameter: target parameter to loop
        The target parameter name is changed to f"{param}_loop"
    """

    @add_modifier_metadata("loop_input", parameter=parameter)
    def loop(func):
        param_list = []
        for param in signature(func).parameters.values():
            if param.name == parameter:
                param_list.append(Parameter(f"{param}_loop", kind=1))
            else:
                param_list.append(param)

        new_sig = Signature(param_list)

        @wraps(func)
        def loop_wrapped(**kwargs):
            """Isolate the loop parameter and loop over the values."""
            loop_values = kwargs.pop(f"{parameter}_loop")

            return [func(**kwargs, **{parameter: value}) for value in loop_values]

        loop_wrapped.__signature__ = new_sig
        return loop_wrapped

    return loop


def zip_loop_inputs(parameters: list):
    """Modify function to iterate the parameters pairwise.

    :param list parameters: list of the parameters to loop
        only one parameter is allowed. If a string of the parameters is
        provided, the parameters should be delimited by ", ".
    """

    @add_modifier_metadata("zip_loop_inputs", parameters=parameters)
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

    return zip_loop


def format_time(dt, precision):
    """Format time in seconds to a human-readable string."""

    units = {"s": 1.0, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
    for unit, scale in units.items():
        if dt >= scale:
            return f"{dt / scale:.{precision}f} {unit}"


def profile_time(number=1, repeat=1, verbose=False, precision=2):
    """Profile the execution time of a function.

    The modifier behaves similarly to the *timeit* module. However,
    the modifier does not suppress garbage collection during the function
    execution; therefore, the result might be slightly different.
    """
    import timeit

    timer = timeit.default_timer

    @add_modifier_metadata(
        "zip_loop_inputs",
        number=number,
        repeat=repeat,
        verbose=verbose,
        precision=precision,
    )
    def timeit_modifier(func):
        @wraps(func)
        def wrapped(**kwargs):
            time_list = []

            for _ in range(repeat):
                t0 = timer()
                for _ in range(number):
                    result = func(**kwargs)
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

    return timeit_modifier


def parse_fields(format_str):
    """Parse the field from the format string.

    :param str format_str: format string
    :return: list of fields

    The function parses out the field names in the format string.
    Some field names have slicers or attribute access, such as
    B0.value, B0[0], B0[0:2]. The function only returns B0 for all
    these fields. Since there can be duplicated fields after the
    name split, the function returns unique elements.
    """

    # this is an internal function for Formatter
    # consider rewriting with custom function to prevent breaking
    # the function ignores slicing and attribute access
    # B0.value -> B0, B0[0] -> B0
    from _string import formatter_field_name_split

    fields = [
        formatter_field_name_split(field)[0]
        for _, field, _, _ in Formatter().parse(format_str)
        if field
    ]
    return list(set(fields))  # return unique elements


def print_inputs(format_str: str, **pargs):
    """Print the node input to the console.

    :param str stdout_format: format string for input and output
        The format should be keyword only.
    :param pargs: keyword arguments for the print function

    The names of the parameters are parsed from the format string.
    """

    @add_modifier_metadata("print_inputs", format_str=format_str, **pargs)
    def stdout_inputs_modifier(func):
        inputs = parse_fields(format_str)

        @wraps(func)
        def wrapped(**kwargs):
            """Print input parameter."""
            input_dict = {k: kwargs[k] for k in inputs}
            print(format_str.format(**input_dict), **pargs)
            return func(**kwargs)

        return wrapped

    return stdout_inputs_modifier


def print_output(format_str: str, **pargs):
    """Print the node output to the console.

    :param str stdout_format: format string for input and output
        The format should be keyword only. The behavior is for keeping the
        consistency with other print modifiers.
    :param str end: end of printout

    The names of the parameters are parsed from the format string. The
    use of the stdout_format is different from the input method, as
    the modifiers do not know the return name of the node. Only one
    output field is allowed and the field name is used as the return name.
    """

    @add_modifier_metadata("print_output", format_str=format_str, **pargs)
    def stdout_output_modifier(func):
        output = parse_fields(format_str)[0]

        @wraps(func)
        def wrapped(**kwargs):
            """Print output parameter."""

            result = func(**kwargs)
            print(format_str.format(**{output: result}), **pargs)
            return result

        return wrapped

    return stdout_output_modifier
