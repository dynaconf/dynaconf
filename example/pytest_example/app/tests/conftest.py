import pytest

from dynaconf import Dynaconf

settings = Dynaconf(**options)


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
