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
