import pytest
from inject_it import requires, provider, exceptions as exc, register_dependency
from tests.conftest import T


def test_requires_decorator_must_be_called_on_function():
    with pytest.raises(exc.InvalidFunctionDecoration):

        @requires  # Missing brackets
        def f():
            pass

        f("Abc")


def test_requires_decorator_must_receive_at_least_one_type():
    with pytest.raises(exc.InvalidFunctionDecoration):

        @requires()
        def f():
            pass


def test_requires_decorator_must_have_dependency_type_annotated_on_decorated_signature():
    with pytest.raises(exc.InvalidFunctionSignature):

        @requires(float)
        def f(a: str):
            pass

        f("abc")


def test_requires_decorator_does_not_allow_duplicated_annotation_for_dependency_type():
    with pytest.raises(exc.InvalidFunctionSignature):

        @requires(T)
        def f(t: T, other_t: T):
            pass

        f()


def test_requires_decorator_does_not_allow_override_of_already_given_keyword_argument():
    with pytest.raises(exc.InjectedKwargAlreadyGiven):

        @requires(T)
        def f(t: T):
            pass

        t = T()
        register_dependency(t)
        f(t=t)


def test_requires_decorator_will_inject_parameter_to_function():
    @requires(T)
    def f(t: T):
        pass

    register_dependency(T())
    f()


def test_requires_decorator_positional_and_keyword_calls():
    @requires(T)
    def f(a: str, b: int, c: float, t: T):
        pass

    register_dependency(T())
    f("123", 1, 1.0)
    f(a="123", b=1, c=1.0)


def test_requires_decorator_can_require_superclass():
    class Concrete(T):
        pass

    c = Concrete()
    register_dependency(c, bound_type=T)

    @requires(T)
    def f(t: T):
        pass

    f()


@pytest.mark.asyncio
async def test_requires_can_also_wraps_coroutine():
    @requires(T)
    async def f(t: T):
        pass

    register_dependency(T())
    await f()


def test_provider_decorator_must_be_called_on_function():
    with pytest.raises(exc.InvalidFunctionDecoration):

        @provider  # Missing brackets
        def f():
            pass

        f("Abc")


def test_provider_decorator_expects_value_from_the_same_type_as_decorated():
    with pytest.raises(exc.ProviderReturnValueTypeMismatch):

        @provider(T)
        def provider_fnc():
            return "123"

        @requires(T)
        def f(t: T):
            return t

        f()


def test_provider_decorator_will_cache_dependency_if_set():
    expected = "123"
    results = [expected, None]

    @provider(str, cache_dependency=True)
    def provider_fnc():
        return results.pop(0)

    @requires(str)
    def f(s: str):
        return s

    for _ in range(10):
        result = f()
        assert result == expected


def test_provider_function_can_also_require_for_dependencies():

    service_fake_key: str = "ABC"
    register_dependency(service_fake_key)

    @provider(T)
    @requires(str)
    def api_provider(service_key: str):
        return T()

    @requires(T)
    def f(t: T):
        return

    f()


def test_provider_decorator_can_provide_superclass():
    class Z(T):
        pass

    @provider(T)
    def z_provider():
        return Z()

    @requires(T)
    def f(t: T):
        return

    f()
