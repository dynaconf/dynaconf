from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.toml", environments=True)

print(settings.A)
print(settings.B)
print(settings.NAMESPACE.A)
print(settings.NAMESPACE.B)
