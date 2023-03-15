from __future__ import annotations

import subprocess

import pytest


@pytest.mark.parametrize(
    "config_option, validator_file",
    (
        (
            pytest.param(
                "config.settings_envs",
                "validators_envs.toml",
                id="with-envs-true",
            ),
            pytest.param(
                "config.settings_noenvs",
                "validators_noenvs.toml",
                id="with-envs-false",
            ),
            pytest.param(
                "config.settings_noenvs",
                "validators_noenvs_only_quoted.toml",
                id="with-quoted-type-only",
            ),
        )
    ),
)
def test_validates_correctly(config_option, validator_file):
    cmd = ("dynaconf", "-i", config_option, "validate", "-p", validator_file)
    result = subprocess.run(cmd, text=True, capture_output=True)
    stdout = result.stdout.lower()
    assert "validation success" in stdout
    assert "invalid rule for parameter" not in stdout


@pytest.mark.parametrize(
    "config_option, validator_file",
    (
        (
            pytest.param(
                "config.settings_envs_invalid",
                "validators_envs.toml",
                id="with-envs-true",
            ),
            pytest.param(
                "config.settings_noenvs_invalid",
                "validators_noenvs.toml",
                id="with-envs-false",
            ),
        )
    ),
)
def test_invalidates_correctly(config_option, validator_file):
    cmd = ("dynaconf", "-i", config_option, "validate", "-p", validator_file)
    result = subprocess.run(cmd, text=True, capture_output=True)
    stdout = result.stdout.lower()
    assert "error" in stdout
    assert "validation success" not in stdout
