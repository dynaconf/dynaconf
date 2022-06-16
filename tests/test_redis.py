from __future__ import annotations

import os

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.redis_loader import delete
from dynaconf.loaders.redis_loader import load
from dynaconf.loaders.redis_loader import write


def custom_checker(ip_address, port):
    # This function should be check if the redis server is online and ready
    # write(settings, {"SECRET": "redis_works"})
    # return load(settings, key="SECRET")
    return True


DYNACONF_TEST_REDIS_URL = os.environ.get("DYNACONF_TEST_REDIS_URL", None)
if DYNACONF_TEST_REDIS_URL:

    @pytest.fixture(scope="module")
    def docker_redis():
        return DYNACONF_TEST_REDIS_URL

else:

    @pytest.fixture(scope="module")
    def docker_redis(docker_services):
        docker_services.start("redis")
        public_port = docker_services.wait_for_service(
            "redis", 6379, check_server=custom_checker
        )
        url = f"http://{docker_services.docker_ip}:{public_port}"
        return url


@pytest.mark.integration
def test_redis_not_configured():
    with pytest.raises(RuntimeError) as excinfo:
        settings = LazySettings(environments=True)
        write(settings, {"OTHER_SECRET": "redis_works"})
    assert "export REDIS_ENABLED_FOR_DYNACONF=true" in str(excinfo.value)


@pytest.mark.integration
def test_write_redis_without_data(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)
    with pytest.raises(AttributeError) as excinfo:
        write(settings)
    assert "Data must be provided" in str(excinfo.value)


@pytest.mark.integration
def test_write_to_redis(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)

    write(settings, {"SECRET": "redis_works_with_docker"})
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "redis_works_with_docker"


@pytest.mark.integration
def test_load_from_redis_with_key(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "redis_works_with_docker"


@pytest.mark.integration
def test_write_and_load_from_redis_without_key(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "redis_works_perfectly"})
    load(settings)
    assert settings.get("SECRET") == "redis_works_perfectly"


@pytest.mark.integration
def test_delete_from_redis(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)
    write(settings, {"OTHER_SECRET": "redis_works"})
    load(settings)
    assert settings.get("OTHER_SECRET") == "redis_works"
    delete(settings, key="OTHER_SECRET")
    assert load(settings, key="OTHER_SECRET") is None


@pytest.mark.integration
def test_delete_all_from_redis(docker_redis):
    settings = LazySettings(environments=True)
    delete(settings)
    assert load(settings, key="OTHER_SECRET") is None
