import inspect
from typing import Any, Optional
from . import _checks
from .exceptions import (
    DependencyNotRegistered,
    InvalidDependency,
    InvalidFunctionSignature,
)
from .objects import Provider
from .stubs import Class, Dependencies, Providers, Types, Kwargs


dependencies: Dependencies = {}
providers: Providers = {}


def _get_dependency(t: Class) -> Optional[Any]:
    dep = dependencies.get(t, Ellipsis)
    if dep is not Ellipsis:
        return dep
    return None


def _get_provider(t: Class) -> Provider:
    provider = providers.get(t)
    if not provider:
        raise DependencyNotRegistered(
            f"Could not found an dependency for: {t}. Did you forgot to register it?"
        )
    return provider


def _resolve_dependency(t: Class) -> Any:
    from inject_it.register import register_dependency

    dep = _get_dependency(t)
    if dep:
        return dep
    provider = _get_provider(t)

    try:
        dependency = provider.fnc()
    except TypeError as e:
        raise InvalidDependency(
            "Could not properly call the provider function.",
            "If the provider requires additional arguments, don't forget to wrap your function call in `additional_kwargs_to_provider`.",
            "Or maybe you forgot to `requires` some dependency on the provider?",
        ) from e
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

    return {param_for_type[t]: _resolve_dependency(t) for t in types}
