import pytest
from inject_it.register import register_dependency
from inject_it import (
    exceptions as exc,
    provider,
    requires,
    additional_kwargs_to_provider,
    register_provider_modules,
)
from tests.conftest import T


def test_register_dependency_will_fail_for_a_object_with_bound_type_that_is_not_subclass():
    class Other:
        pass

    with pytest.raises(exc.InvalidDependency):
        register_dependency(T(), bound_type=Other)


def test_register_dependency_succeeds_for_object_that_is_subclass():
    class Z(T):
        pass

    register_dependency(Z(), bound_type=T)


def test_additional_kwargs_for_provider_succeeds_for_correct_call():
    class Client:
        def __init__(self, key):
            self.key = key

    @provider(Client)
    def conditional_t_provider(key: str):
        return Client(key)

    @requires(Client)
    def f(c: Client):
        return c.key

    with additional_kwargs_to_provider(Client, key="ABC"):
        key = f()
        assert key == "ABC"

    # Should rollback, and since we'are not passing any arguments to the provider
    # should fail.
    with pytest.raises(exc.InvalidDependency):
        f()


def test_register_provider_modules_raises_for_no_provider_in_module():
    with pytest.raises(exc.InvalidDependency):
        register_provider_modules("tests.test_decorators")
