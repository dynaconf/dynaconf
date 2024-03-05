from __future__ import annotations

import os

import pytest

from dynaconf import LazySettings

TOML = """
[global]
var = "my value"

[false]
thisvar = "should not be set"
"""


def test_envvar_prefix_lazysettings(tmpdir):
    os.environ["DYNACONF_PREFIXED_VAR"] = "this is prefixed"
    tmpfile = tmpdir.mkdir("sub").join("test_no_envvar_prefix.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True,
        envvar_prefix=False,
        settings_file=str(tmpfile),
    )

    assert settings.VAR == "my value"
    assert settings.DYNACONF_PREFIXED_VAR == "this is prefixed"


def test_envvar_prefix_false_from_envvar(tmpdir):
    os.environ["DYNACONF_PREFIXED_VAR"] = "this is prefixed"
    os.environ["ENVVAR_PREFIX_FOR_DYNACONF"] = "false"
    tmpfile = tmpdir.mkdir("sub").join("test_no_envvar_prefix.toml")
    tmpfile.write(TOML)

    settings = LazySettings(environments=True, settings_file=str(tmpfile))

    assert settings.VAR == "my value"
    assert settings.DYNACONF_PREFIXED_VAR == "this is prefixed"

    with pytest.raises(AttributeError):
        assert settings.THISVAR == "should not be set"
    del os.environ["ENVVAR_PREFIX_FOR_DYNACONF"]
