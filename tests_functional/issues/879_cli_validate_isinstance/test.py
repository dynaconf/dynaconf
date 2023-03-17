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


@pytest.mark.parametrize(
    "validator_file, error_msg",
    (
        (
            pytest.param(
                "validators_invalid_toml.toml",
                "error parsing toml",
                id="invalid-toml-token",
            ),
            pytest.param(
                "validators_invalid_type.toml",
                "error: invalid type",
                id="invalid-builtin-type",
            ),
        )
    ),
)
def test_wrong_validator_rule_gives_error_msg_correctly(
    validator_file, error_msg
):
    cmd = (
        "dynaconf",
        "-i",
        "config.settings_noenvs",
        "validate",
        "-p",
        validator_file,
    )
    result = subprocess.run(cmd, text=True, capture_output=True)
    stdout = result.stdout.lower()
    assert error_msg in stdout
    assert "validation success" not in stdout
