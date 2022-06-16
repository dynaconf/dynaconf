from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.yaml",
    environments=True,
)

print(settings.current_env)
print(settings._loaded_by_loaders)

assert (
    settings.get("www.google.com", dotted_lookup=False) == "data"
), settings.get("www.google.com")
assert settings.as_dict() == {"WWW.GOOGLE.COM": "data"}, settings.as_dict()
