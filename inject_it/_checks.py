import inspect
from typing import Any

from .exceptions import (
    InjectedKwargAlreadyGiven,
    InvalidFunctionSignature,
    InvalidFunctionDecoration,
    ProviderReturnValueTypeMismatch,
)
from .stubs import Kwargs, Types, Class


def wrapped_callable(fnc):
    if not callable(fnc):
        raise InvalidFunctionDecoration(
            "Did you forgot to call the decorator in the wrapped function?"
        )


def at_least_one_type_required(*types: Class):
    if not types:
        raise InvalidFunctionDecoration("At least one type is required to be injected.")


def provider_returned_expected_type(obj: Any, type_: Class):
    if type(obj) is not type_ and not issubclass(obj.__class__, type_):
        raise ProviderReturnValueTypeMismatch(
            f"Invalid return type. Expected {type_} or subclass of it, but received: {type(obj)}"
        )


def no_duplicated_type_annotation_for_types_on_sig(
    sig: inspect.Signature, types: Types
):
    types_annotations = [
        s.annotation for s in sig.parameters.values() if s.annotation in types
    ]
    non_duplicated_annotations = set(types_annotations)
    if len(non_duplicated_annotations) != len(types_annotations):
        raise InvalidFunctionSignature(
            "The function signature has duplicated dependencies type definitions"
        )


def no_injected_and_called_kwarg(original_kwargs: Kwargs, injected_kwargs: Kwargs):
    for inj_kw in injected_kwargs:
        if inj_kw in original_kwargs:
            raise InjectedKwargAlreadyGiven(
                f"The argument: {inj_kw} cannot be injected, it was already given somewhere else."
            )
