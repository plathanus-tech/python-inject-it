import inspect
from functools import wraps
from typing import Callable, Any

from inject_it.register import register_provider

from .stubs import Class, DecoratedFunction, Function
from ._injector import get_injected_kwargs_for_signature
from . import _checks


def _helper(fnc, *args, **kwargs) -> Any:
    if inspect.iscoroutinefunction(fnc):

        async def f():
            return await (fnc(*args, **kwargs))

        return f()
    return fnc(*args, **kwargs)


def requires(*types: Class):
    """Decorates a function and on runtime injects the dependencies for the given `types` into the
    function. The dependency will be injected on the parameter that has a type annotation for the
    matching type. The others typed/non-typed arguments that has no match to types will remain from
    your original call.

    Usage:

    ```python

    @requires(str, int)
    def your_func(required_arg: float, some_arg: str, other_arg: int):
        ...

    # Later ...

    # Calling using keyword arguments
    your_func(required_arg=1.0)

    # Positional arguments
    your_func(1.0)

    ```
    """

    def decorator(
        fnc: DecoratedFunction,
    ) -> Callable[[DecoratedFunction], Function]:
        _checks.wrapped_callable(fnc)
        _checks.at_least_one_type_required(*types)
        sig = inspect.signature(fnc)
        _checks.no_duplicated_type_annotation_for_types_on_sig(sig=sig, types=types)

        @wraps(fnc)
        def decorated(*args, **kwargs):
            injected_kwargs = get_injected_kwargs_for_signature(sig=sig, types=types)
            _checks.no_injected_and_called_kwarg(
                original_kwargs=kwargs, injected_kwargs=injected_kwargs
            )
            kwargs.update(injected_kwargs)
            return _helper(fnc, *args, **kwargs)

        return decorated

    return decorator


def provider(type_: Class, cache_dependency: bool = False):
    """Register a function that should return a dependency for the given type.
    If `cache_dependency` is `True` then the function will be only called once.
    """

    def decorator(
        fnc: DecoratedFunction,
    ) -> Callable[[DecoratedFunction], Function]:
        _checks.wrapped_callable(fnc)
        register_provider(
            type_=type_,
            fnc=fnc,
            cache_dependency=cache_dependency,
        )

        @wraps(fnc)
        def decorated(*args, **kwargs):
            return _helper(fnc, *args, **kwargs)

        return decorated

    return decorator
