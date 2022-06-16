from __future__ import annotations

import os

from dynaconf import LazySettings


TOML = """
[default]
DATA = true

[premiumuser]
DASHBOARD="True"

[simpleuser]
DASHBOARD=false
"""


def test_feature_flag(tmpdir):

    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(environments=True, settings_file=str(tmpfile))

    assert settings.flag("dashboard", "premiumuser") is True
    assert settings.flag("dashboard", "simpleuser") is False
    assert settings.flag("dashboard") is False

    # ensure data is fresh
    os.environ["DYNACONF_DASHBOARD"] = "@bool on"
    assert settings.flag("dashboard") is True

    os.environ["DYNACONF_DASHBOARD"] = "False"
    assert settings.flag("dashboard") is False
