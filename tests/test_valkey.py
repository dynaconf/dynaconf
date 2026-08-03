from __future__ import annotations

import os
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.valkey_loader import delete
from dynaconf.loaders.valkey_loader import load
from dynaconf.loaders.valkey_loader import write
from dynaconf.utils.inspect import get_history

if TYPE_CHECKING:
    from pytest_docker.plugin import Service


def is_responsive(url):
    # This function should check if the valkey server is online and ready
    # write(settings, {"SECRET": "valkey_works"})
    # return load(settings, key="SECRET")
    return True


DYNACONF_TEST_VALKEY_URL = os.environ.get("DYNACONF_TEST_VALKEY_URL", None)
if DYNACONF_TEST_VALKEY_URL:

    @pytest.fixture(scope="module")
    def docker_valkey():
        return DYNACONF_TEST_VALKEY_URL

else:

    @pytest.fixture(scope="module")
    def docker_valkey(docker_ip: str, docker_services: Iterator[Service]):
        port = docker_services.port_for("valkey", 6379)
        url = f"http://{docker_ip}:{port}"
        docker_services.wait_until_responsive(
            timeout=15.0, pause=0.1, check=lambda: is_responsive(url)
        )
        return url


@pytest.mark.integration
def test_valkey_not_configured():
    with pytest.raises(RuntimeError) as excinfo:
        settings = LazySettings(environments=True)
        write(settings, {"OTHER_SECRET": "valkey_works"})
    assert "export VALKEY_ENABLED_FOR_DYNACONF=true" in str(excinfo.value)


@pytest.mark.integration
def test_write_valkey_without_data(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)
    with pytest.raises(AttributeError) as excinfo:
        write(settings)
    assert "Data must be provided" in str(excinfo.value)


@pytest.mark.integration
def test_write_to_valkey(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)

    write(settings, {"SECRET": "valkey_works_with_docker"})
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "valkey_works_with_docker"


@pytest.mark.integration
def test_load_from_valkey_with_key(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "valkey_works_with_docker"


@pytest.mark.integration
def test_write_and_load_from_valkey_without_key(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "valkey_works_perfectly"})
    load(settings)
    assert settings.get("SECRET") == "valkey_works_perfectly"


@pytest.mark.integration
def test_delete_from_valkey(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)
    write(settings, {"OTHER_SECRET": "valkey_works"})
    load(settings)
    assert settings.get("OTHER_SECRET") == "valkey_works"
    delete(settings, key="OTHER_SECRET")
    assert load(settings, key="OTHER_SECRET") is None


@pytest.mark.integration
def test_delete_all_from_valkey(docker_valkey):
    settings = LazySettings(environments=True)
    delete(settings)
    assert load(settings, key="OTHER_SECRET") is None


@pytest.mark.integration
def test_valkey_has_proper_source_metadata(docker_valkey):
    os.environ["VALKEY_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VALKEY_HOST_FOR_DYNACONF"] = "localhost"
    os.environ["VALKEY_PORT_FOR_DYNACONF"] = "16379"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "valkey_works_perfectly"})
    load(settings)
    history = get_history(
        settings, filter_callable=lambda s: s.loader == "valkey"
    )
    assert history[0]["env"] == "development"  # default when environments=True
    assert history[0]["value"]["SECRET"] == "valkey_works_perfectly"
