from __future__ import annotations

import base64
import json
import os
import subprocess
import time
from collections.abc import Iterator
from typing import TYPE_CHECKING

import hvac
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


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _sign_test_jwt(tmp_path, claims: dict) -> str:
    """A self-signed RS256 JWT, built with openssl only (no PyJWT test dep)."""
    private_key = tmp_path / "jwt_test_key.pem"
    subprocess.run(
        ["openssl", "genrsa", "-out", str(private_key), "2048"],
        check=True,
        capture_output=True,
    )
    public_key = subprocess.run(
        ["openssl", "rsa", "-in", str(private_key), "-pubout"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    header = {"alg": "RS256", "typ": "JWT"}
    signing_input = (
        f"{_b64url(json.dumps(header).encode())}."
        f"{_b64url(json.dumps(claims).encode())}"
    )
    signature = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(private_key)],
        input=signing_input.encode(),
        capture_output=True,
        check=True,
    ).stdout
    return f"{signing_input}.{_b64url(signature)}", public_key


@pytest.mark.integration
def test_load_from_vault_with_jwt_auth(docker_vault, tmp_path):
    """A CI-issued JWT (GitLab id_tokens, k8s service account tokens, ...)
    authenticates via Vault's jwt auth method - no VAULT_TOKEN involved."""
    now = int(time.time())
    test_jwt, public_key = _sign_test_jwt(
        tmp_path,
        {
            "sub": "dynaconf-ci",
            "aud": "dynaconf-tests",
            "iat": now,
            "exp": now + 300,
        },
    )

    root = hvac.Client(url=docker_vault, token="myroot")
    root.sys.enable_auth_method("jwt", path="jwt-test")
    root.auth.jwt.configure(
        jwt_validation_pubkeys=[public_key], path="jwt-test"
    )
    root.sys.create_or_update_policy(
        name="dynaconf-jwt-test",
        policy='path "secret/*" { capabilities = ["read", "list", "create", "update"] }',
    )
    root.auth.jwt.create_role(
        name="dynaconf-role",
        role_type="jwt",
        allowed_redirect_uris=[],
        bound_audiences=["dynaconf-tests"],
        user_claim="sub",
        bound_subject="dynaconf-ci",
        token_policies=["dynaconf-jwt-test"],
        path="jwt-test",
    )

    os.environ["VAULT_ENABLED_FOR_DYNACONF"] = "1"
    os.environ["VAULT_URL_FOR_DYNACONF"] = docker_vault
    os.environ["VAULT_KV_VERSION_FOR_DYNACONF"] = "1"
    os.environ["VAULT_PATH_FOR_DYNACONF"] = "test_jwt_auth"
    os.environ["VAULT_TOKEN_FOR_DYNACONF"] = "myroot"
    settings = LazySettings(environments=True)
    write(settings, {"SECRET": "vault_works_with_jwt"})

    del os.environ["VAULT_TOKEN_FOR_DYNACONF"]
    os.environ["VAULT_JWT_TOKEN_FOR_DYNACONF"] = test_jwt
    os.environ["VAULT_JWT_AUTH_PATH_FOR_DYNACONF"] = "jwt-test"
    os.environ["VAULT_AUTH_ROLE_FOR_DYNACONF"] = "dynaconf-role"
    settings = LazySettings(environments=True)
    load(settings, key="SECRET")
    assert settings.get("SECRET") == "vault_works_with_jwt"

    del os.environ["VAULT_JWT_TOKEN_FOR_DYNACONF"]
    del os.environ["VAULT_JWT_AUTH_PATH_FOR_DYNACONF"]
    del os.environ["VAULT_AUTH_ROLE_FOR_DYNACONF"]
