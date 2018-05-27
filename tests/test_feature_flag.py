import pytest
from dynaconf import LazySettings, Validator, ValidationError


TOML = """
[default]
DATA = true

[premiumuser]
DASHBOARD="True"

[simpleuser]
DASHBOARD=false
"""


def test_feature_flag(tmpdir):

    tmpfile = tmpdir.join('settings.toml')
    tmpfile.write(TOML)

    settings = LazySettings(SETTINGS_MODULE_FOR_DYNACONF=str(tmpfile),)

    assert settings.flag('dashboard', 'premiumuser') is True
    assert settings.flag('dashboard', 'simpleuser') is False
    assert settings.flag('dashboard') is False
