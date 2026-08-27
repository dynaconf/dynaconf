from __future__ import annotations

import os
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from dynaconf import LazySettings
from dynaconf.loaders.redis_loader import delete
from dynaconf.loaders.redis_loader import load
from dynaconf.loaders.redis_loader import write
from dynaconf.utils.inspect import get_history

if TYPE_CHECKING:
    from pytest_docker.plugin import Service


def is_responsive(host, port):
    try:
        return redis.Redis(
            host=host, port=port, socket_connect_timeout=2
        ).ping()
    except RedisConnectionError:
        return False


DYNACONF_TEST_REDIS_URL = os.environ.get("DYNACONF_TEST_REDIS_URL", None)
if DYNACONF_TEST_REDIS_URL:

    @pytest.fixture(scope="module")
    def docker_redis():
        return DYNACONF_TEST_REDIS_URL

else:

    @pytest.fixture(scope="module")
    def docker_redis(docker_ip: str, docker_services: Iterator[Service]):
        port = docker_services.port_for("redis", 6379)
        url = f"http://{docker_ip}:{port}"
        docker_services.wait_until_responsive(
            timeout=15.0,
            pause=0.1,
            check=lambda: is_responsive(docker_ip, port),
        )
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


@pytest.mark.integration
def test_redis_has_proper_source_metadata(docker_redis):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "redis_works_perfectly"})
    load(settings)
    history = get_history(
        settings, filter_callable=lambda s: s.loader == "redis"
    )
    assert history[0]["env"] == "development"  # default when environments=True
    assert history[0]["value"]["SECRET"] == "redis_works_perfectly"


@pytest.mark.parametrize("use_settings_kwarg", [True, False])
@pytest.mark.integration
def test_write_to_redis_via_loaders_write_facade(
    docker_redis, use_settings_kwarg
):
    os.environ["REDIS_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["REDIS_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["REDIS_PORT_FOR_DYNACONF"] = "6379"
    settings = LazySettings(environments=True)

    from dynaconf import loaders
    from dynaconf.loaders.redis_loader import _get_redis_client

    # We must reset the loader to test both cleanly if needed, but here just calling is fine
    if use_settings_kwarg:
        loaders.write(
            "redis",
            {f"KEY_{use_settings_kwarg}": "value"},
            env="DEVELOPMENT",
            settings=settings,
        )
    else:
        loaders.write(
            "redis", {f"KEY_{use_settings_kwarg}": "value"}, env="DEVELOPMENT"
        )

    client = _get_redis_client(settings)
    holder = (
        f"{settings.get('ENVVAR_PREFIX_FOR_DYNACONF')}_DEVELOPMENT".upper()
    )

    val = client.hget(holder, f"KEY_{use_settings_kwarg}".upper())
    assert val is not None, (
        "Value not persisted in Redis backend in the DEVELOPMENT namespace"
    )
    assert b"value" in val, "Precise value was not found in Redis"

    # Assert it natively via the public API
    from dynaconf.loaders.redis_loader import load

    with settings.using_env("DEVELOPMENT"):
        load(settings)
        assert settings.get(f"KEY_{use_settings_kwarg}") == "value"

    # Assert the data schema is flat (not nested under 'DEVELOPMENT')
    nested = client.hget(holder, "DEVELOPMENT")
    assert nested is None, "Data schema is nested under 'DEVELOPMENT'"
