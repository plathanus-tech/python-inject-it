import inspect
from typing import Any, Type
from . import _checks
from .exceptions import DependencyNotRegistered, InvalidFunctionSignature
from .stubs import Dependencies, Providers, Types, Kwargs


dependencies: Dependencies = {}
providers: Providers = {}


def _get_dependency(t: Type) -> Any:
    from inject_it.register import register_dependency

    dep = dependencies.get(t, Ellipsis)
    if dep is not Ellipsis:
        return dep

    provider = providers.get(t)
    if not provider:
        raise DependencyNotRegistered(
            f"Could not found an dependency for: {t}. Did you forgot to register it?"
        )
    dependency = provider.fnc()
    _checks.provider_returned_expected_type(
        obj=dependency, type_=provider.expected_return_type
    )
    if provider.cache_dependency:
        register_dependency(dependency)
    return dependency


def get_injected_kwargs_for_signature(sig: inspect.Signature, types: Types) -> Kwargs:
    param_for_type = {s.annotation: p for p, s in sig.parameters.items()}
    for typ in types:
        if typ not in param_for_type:
            raise InvalidFunctionSignature(
                f"The type {typ} was not found on the function signature. Did you forgot to type annotate it?"
            )

    return {param_for_type[t]: _get_dependency(t) for t in types}
