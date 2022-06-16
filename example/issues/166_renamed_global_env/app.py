from __future__ import annotations

from dynaconf import settings

assert settings.ENVVAR_PREFIX_FOR_DYNACONF == "GREATAPP"
assert settings.GLOBAL_ENV_FOR_DYNACONF == "GREATAPP"
assert settings.INT == 1
assert settings.FLOAT == 42.2
assert settings.LIST == ["a", "b"]
assert settings.BOOL is False
assert settings.DICT.NAME == "dynaconf"

for key in ["INT", "FLOAT", "LIST", "BOOL", "DICT", "DICT.NAME", "NOWAY"]:
    print(settings.get(key, None))  # noqa
