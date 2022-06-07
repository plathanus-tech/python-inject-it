import pytest
from inject_it.register import register_dependency
from inject_it import exceptions as exc
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
