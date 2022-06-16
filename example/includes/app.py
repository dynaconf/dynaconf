from __future__ import annotations

from dynaconf import settings

assert settings.DYNACONF_INCLUDE == [
    "configs/*",
    "this_is_not_loaded.toml",
], settings.DYNACONF_INCLUDE
assert settings.SETTINGS_VAR is True
assert settings.LASTFILE == "configs/plugin4.py"
assert settings.MERGEABLE == {
    "plugin1": True,
    "plugin2": True,
    "plugin3": True,
    "plugin4": True,
    "settings": True,
}, settings.MERGEABLE
assert settings.PLUGIN1_VAR is True
assert settings.PLUGIN2_VAR is True
assert settings.PLUGIN3_VAR is True
assert settings.PLUGIN4_VAR is True
