from __future__ import annotations

import os
from collections.abc import Iterator
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
import requests

from dynaconf import LazySettings
from dynaconf.loaders.vault_loader import list_envs
from dynaconf.loaders.vault_loader import load
from dynaconf.loaders.vault_loader import write
from dynaconf.utils.inspect import get_history

if TYPE_CHECKING:
    from pytest_docker.plugin import Service


def is_responsive(url):
    try:
        response = requests.get(f"{url}/v1/sys/health", timeout=2)
    except requests.exceptions.ConnectionError:
        return False
    return response.status_code == 200


@pytest.fixture(scope="module")
def docker_vault(docker_ip: str, docker_services: Iterator[Service]):
    public_port = docker_services.port_for("vault", 8200)
    url = f"http://{docker_ip}:{public_port}"
    docker_services.wait_until_responsive(
        timeout=15.0, pause=3, check=lambda: is_responsive(url)
    )
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


@pytest.mark.integration
def test_vault_has_proper_source_metadata(docker_vault):
    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_KV_VERSION_FOR_DYNACONF"] = "2"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=["dev", "prod"])
    for env in ["default", "dev", "prod"]:
        with settings.using_env(env):
            write(settings, {"SECRET": f"vault_works_in_{env}"})
    load(settings)
    history = get_history(
        settings, filter_callable=lambda s: s.loader == "vault"
    )
    assert history[0]["env"] == "default"
    assert history[0]["value"]["SECRET"] == "vault_works_in_default"
    assert history[1]["env"] == "dev"
    assert history[1]["value"]["SECRET"] == "vault_works_in_dev"
    assert history[2]["env"] == "prod"
    assert history[2]["value"]["SECRET"] == "vault_works_in_prod"


@pytest.fixture(params=[1, 2], ids=["kv1", "kv2"])
def vault_environment_loader(request, monkeypatch):
    for name in tuple(os.environ):
        if name.endswith("_FOR_DYNACONF"):
            monkeypatch.delenv(name)

    client = Mock()
    monkeypatch.setattr(
        "dynaconf.loaders.vault_loader.get_client", lambda obj: client
    )
    settings = LazySettings(
        environments=True,
        env="dev",
        envvar_prefix="DYNACONF",
        default_env="default",
        main_env="main",
        settings_files=[],
        loaders=[],
        load_dotenv=False,
        VAULT_ENABLED_FOR_DYNACONF=False,
        VAULT_KV_VERSION_FOR_DYNACONF=request.param,
        VAULT_PATH_FOR_DYNACONF="dynaconf",
        VAULT_MOUNT_POINT_FOR_DYNACONF="secret",
    )
    settings.SETTING = "local-dev"
    kv = client.secrets.kv
    api = kv.v2 if request.param == 2 else kv.v1
    list_secrets = api.list_secrets
    list_secrets.return_value = {"data": {"keys": ["prod"]}}
    read_secret = (
        kv.v2.read_secret_version if request.param == 2 else kv.read_secret
    )
    secrets = {
        "default": {"FALLBACK": "default"},
        "dynaconf": {"ORDER": "prefix"},
        "dev": {"ORDER": "dev"},
        "qa": {"ORDER": "qa"},
        "global": {"ORDER": "global"},
        "prod": {"SETTING": "production", "PROD_ONLY": "production"},
        "main": {"ORDER": "main"},
        "": {"ORDER": "root"},
    }

    def read(path, **kwargs):
        data = secrets[path.rsplit("/", 1)[-1]].copy()
        if request.param == 2 and settings.ENVIRONMENTS_FOR_DYNACONF:
            data = {"data": data}
        return {"data": {"data": data}}

    read_secret.side_effect = read
    return settings, list_secrets, read_secret


def test_vault_load_all_envs_default(vault_environment_loader):
    settings, list_secrets, _ = vault_environment_loader
    assert settings.VAULT_LOAD_ALL_ENVS_FOR_DYNACONF is True

    load(settings)

    list_secrets.assert_called_once_with(path="dynaconf", mount_point="secret")
    assert settings.SETTING == "production"
    assert settings.PROD_ONLY == "production"
    assert settings.ORDER == "global"


def test_vault_load_all_envs_disabled(vault_environment_loader):
    settings, list_secrets, read_secret = vault_environment_loader
    settings.VAULT_LOAD_ALL_ENVS_FOR_DYNACONF = False

    load(settings)

    list_secrets.assert_not_called()
    assert settings.SETTING == "local-dev"
    assert settings.get("PROD_ONLY") is None
    assert settings.FALLBACK == "default"
    assert settings.ORDER == "global"
    paths = [args.args[0] for args in read_secret.call_args_list]
    assert [path.rsplit("/", 1)[-1] for path in paths] == [
        "default",
        "dynaconf",
        "dev",
        "global",
    ]
    history = get_history(
        settings, filter_callable=lambda source: source.loader == "vault"
    )
    assert {item["env"] for item in history} == {
        "default",
        "dynaconf",
        "dev",
        "global",
    }


def test_vault_load_all_envs_disabled_key(vault_environment_loader):
    settings, list_secrets, _ = vault_environment_loader
    settings.VAULT_LOAD_ALL_ENVS_FOR_DYNACONF = False

    load(settings, key="SETTING")

    list_secrets.assert_not_called()
    assert settings.SETTING == "local-dev"
    assert settings.get("PROD_ONLY") is None
    assert settings.get("ORDER") is None


def test_vault_load_all_envs_explicit_env(vault_environment_loader):
    settings, list_secrets, read_secret = vault_environment_loader
    settings.VAULT_LOAD_ALL_ENVS_FOR_DYNACONF = False

    load(settings, env="qa, dev")

    list_secrets.assert_not_called()
    paths = [args.args[0] for args in read_secret.call_args_list]
    assert [path.rsplit("/", 1)[-1] for path in paths] == [
        "default",
        "dynaconf",
        "dev",
        "qa",
        "global",
    ]
    assert settings.ORDER == "global"


def test_vault_load_all_envs_without_environments(vault_environment_loader):
    settings, list_secrets, read_secret = vault_environment_loader
    settings.VAULT_LOAD_ALL_ENVS_FOR_DYNACONF = False
    settings.ENVIRONMENTS_FOR_DYNACONF = False

    load(settings)

    list_secrets.assert_not_called()
    paths = [args.args[0] for args in read_secret.call_args_list]
    assert [path.rsplit("/", 1)[-1] for path in paths] == ["main", ""]
    assert settings.ORDER == "root"
