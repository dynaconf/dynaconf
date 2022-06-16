from __future__ import annotations

import os
from time import sleep

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.vault_loader import list_envs
from dynaconf.loaders.vault_loader import load
from dynaconf.loaders.vault_loader import write


def custom_checker(ip_address, port):
    # This function should be check if the redis server is online and ready
    # write(settings, {"SECRET": "redis_works"})
    # return load(settings, key="SECRET")
    return True


@pytest.fixture(scope="module")
def docker_vault(docker_services):
    docker_services.start("vault")
    public_port = docker_services.wait_for_service(
        "vault", 8200, check_server=custom_checker
    )
    url = f"http://{docker_services.docker_ip}:{public_port}"

    sleep(3)
    return url


@pytest.mark.integration
def test_load_vault_not_configured():
    with pytest.raises(AssertionError) as excinfo:
        settings = LazySettings(environments=True)
        load(settings, {"OTHER_SECRET": "vault_works"})
    assert "Vault authentication error" in str(excinfo.value)


@pytest.mark.integration
def test_write_vault_not_configured():
    with pytest.raises(RuntimeError) as excinfo:
        settings = LazySettings(environments=True)
        write(settings, {"OTHER_SECRET": "vault_works"})
    assert "export VAULT_ENABLED_FOR_DYNACONF" in str(excinfo.value)


@pytest.mark.integration
def test_write_vault_without_data(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    with pytest.raises(AttributeError) as excinfo:
        write(settings)
    assert "Data must be provided" in str(excinfo.value)


@pytest.mark.integration
def test_list_envs_in_vault(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    envs = list_envs(settings, "test_list_envs_in_vault")
    assert envs == []


@pytest.mark.integration
def test_write_to_vault(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "vault_works_with_docker"})
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "vault_works_with_docker"


@pytest.mark.integration
def test_load_from_vault_with_key(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "vault_works_with_docker"


@pytest.mark.integration
def test_write_and_load_from_vault_without_key(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "vault_works_perfectly"})
    load(settings)
    assert settings.get("SECRET") == "vault_works_perfectly"


@pytest.mark.integration
def test_read_from_vault_kv2_with_different_environments(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_KV_VERSION_FOR_DYNACONF"] = "2"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=["dev", "prod"])
    for env in ["default", "dev", "prod"]:
        with settings.using_env(env):
            write(settings, {"SECRET": f"vault_works_in_{env}"})
    load(settings)
    assert settings.secret == "vault_works_in_default"
    assert settings.from_env("dev").secret == "vault_works_in_dev"
    assert settings.from_env("prod").secret == "vault_works_in_prod"
