from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_files=["settings.toml"])

print(settings.num)
print(type(settings.num))

assert settings.num == -1, settings.num
assert isinstance(settings.num, int)
