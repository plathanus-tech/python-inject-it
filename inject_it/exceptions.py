# Base exceptions


class DependencyNotRegistered(LookupError):
    pass


class InvalidDependency(ValueError):
    pass


class InjectedKwargAlreadyGiven(TypeError):
    pass


class InvalidFunctionSignature(TypeError):
    pass


class InvalidFunctionDecoration(TypeError):
    pass


class ProviderReturnValueTypeMismatch(TypeError):
    pass
