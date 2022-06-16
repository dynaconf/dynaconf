from __future__ import annotations

from dynaconf import settings

assert settings.ENVVAR_PREFIX_FOR_DYNACONF == "GREATAPP"
assert settings.GLOBAL_ENV_FOR_DYNACONF == "GREATAPP"
assert settings.INT == 1
assert settings.FLOAT == 42.2
assert settings.LIST == ["a", "b"]
assert settings.BOOL is False
assert settings.DICT.NAME == "dynaconf"
assert settings.FOOBAR == "baz"

for key in [
    "INT",
    "FLOAT",
    "LIST",
    "BOOL",
    "DICT",
    "DICT.NAME",
    "NOWAY",
    "FOOBAR",
]:
    print(settings.get(key, None))  # noqa


assert settings.SETTINGS_FILE_FOR_DYNACONF == "foo_bar.toml"
assert settings.SETTINGS_MODULE_FOR_DYNACONF == "foo_bar.toml"
assert settings.SETTINGS_MODULE == "foo_bar.toml"
assert settings.settings_module == "foo_bar.toml"
assert settings.DYNACONF_SETTINGS == "foo_bar.toml"
