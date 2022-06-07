import pytest
from inject_it._injector import dependencies, providers


@pytest.fixture(autouse=True)
def auto_clear_dependencies_and_providers():

    dependencies.clear()
    providers.clear()


class T:
    """A stub object"""

    pass
