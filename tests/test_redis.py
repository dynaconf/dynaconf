import io
import os

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.redis_loader import delete
from dynaconf.loaders.redis_loader import load
from dynaconf.loaders.redis_loader import write


def custom_checker(ip_address, port):
    return True


@pytest.fixture(scope="module")
def redis_conf():
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"


@pytest.fixture(scope="module")
def docker_redis(docker_services):
    docker_services.start("redis")
    public_port = docker_services.wait_for_service(
        "redis", 6379, check_server=custom_checker
    )
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


def test_write_to_redis(redis_conf, docker_redis):

    # os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    # os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    # os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings()
    write(settings, {"SECRET": "redis_works"})
    assert settings.get("SECRET") == "redis_works"


def test_load_from_redis(redis_conf, docker_redis):
    settings = LazySettings()
    load(settings)

    assert settings.get("SECRET") == "redis_works"


def test_delete_from_redis(redis_conf, docker_redis):
    settings = LazySettings()
    delete(settings, key="SECRET")

    assert settings.get("SECRET") is None
