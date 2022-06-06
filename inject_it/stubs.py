from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple, Type, TypeVar


if TYPE_CHECKING:
    from .objects import Provider


Class = Type[Any]
Types = Tuple[Class, ...]
Function = Callable[..., Any]
Kwargs = Dict[str, Any]
Dependencies = Dict[Type, Any]
Providers = Dict[Type, "Provider"]
DecoratedFunction = TypeVar("DecoratedFunction", bound=Function)
