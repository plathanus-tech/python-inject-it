from typing import Any
from .objects import Provider
from .stubs import Class, Function
from .exceptions import InvalidDependency


def register_dependency(obj: Any) -> None:
    """Register a given `obj` to be later used by `requires` decorator."""
    from ._injector import dependencies

    obj_type = type(obj)
    if obj_type is type:
        raise InvalidDependency("Can only register objects, not classes")
    dependencies[obj_type] = obj


def register_provider(type_: Class, fnc: Function, cache_dependency: bool) -> None:
    """Register a provider to be later used by `requires` decorator."""
    from ._injector import providers

    providers[type_] = Provider(
        fnc=fnc,
        cache_dependency=cache_dependency,
        expected_return_type=type_,
    )
