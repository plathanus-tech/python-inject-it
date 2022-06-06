from dataclasses import dataclass
from .stubs import Class, Function


@dataclass
class Provider:
    fnc: Function
    cache_dependency: bool
    expected_return_type: Class
