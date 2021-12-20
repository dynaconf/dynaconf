from dynaconf import settings


def pytest_configure(config):
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
