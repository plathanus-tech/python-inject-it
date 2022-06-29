import importlib
from contextlib import contextmanager
from functools import partial
from typing import Any, Optional

from .objects import Provider
from .stubs import Class, Function
from .exceptions import InvalidDependency


def register_dependency(obj: Any, bound_type: Optional[Class] = None) -> None:
    """Register a given `obj` to be later used by `requires` decorator.
    Arguments:
    `obj` Any: The object to be registered.
    `bound_type` Optional[Class]: The type that this object will be bounded. You may want to use `bound_type` if you have
    a `obj` for a concrete instance and want to require/type annotate the abstract type.

    Examples:
    -Bound object to its type:
    `register_dependency(obj)`

    -Bound object to another type:
    `register_dependency(obj, AbcService)`
    """
    from ._injector import dependencies

    obj_type = bound_type or type(obj)
    if obj_type is type:
        raise InvalidDependency("Can only register objects, not classes")
    if bound_type and not issubclass(obj.__class__, bound_type):
        raise InvalidDependency(
            "When registering an object with a `bound_type` make sure that `obj` is a subclass of it."
        )
    dependencies[obj_type] = obj


def register_provider(type_: Class, fnc: Function, cache_dependency: bool) -> None:
    """Register a provider to be later used by `requires` decorator."""
    from ._injector import providers

    providers[type_] = Provider(
        fnc=fnc,
        cache_dependency=cache_dependency,
        expected_return_type=type_,
    )


@contextmanager
def additional_kwargs_to_provider(type_: Class, **kwargs):
    """Context manager that applies the given `kwargs` to the provider function previously registered.
    At the end, rollbacks to the original function. It's useful when your dependency is created on the
    fly using some additional parameters, like the current user in a HTTP Request, the current state of
    some object.
    """
    from ._injector import _get_provider, providers

    provider = _get_provider(type_)

    providers[type_] = Provider(
        fnc=partial(provider.fnc, **kwargs),
        expected_return_type=provider.expected_return_type,
        cache_dependency=provider.cache_dependency,
    )
    yield
    providers[type_] = provider


def register_provider_modules(*modules: str):
    """Shortcut to register all given modules with providers functions.
    The given modules are passed directly to `importlib.import_module', so it must be a valid namespace.
    If no `provider` is registered in a module, then raises `InvalidDependency`.
    """
    from ._injector import providers

    for mod in modules:
        n_of_providers = len(providers)
        importlib.import_module(mod)
        if len(providers) == n_of_providers:
            raise InvalidDependency(
                f"No provider was registered on {mod=} Did you forgot the `provider` decorator?"
            )
