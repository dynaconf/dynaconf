from __future__ import annotations

from dynaconf import settings

print(settings.DEBUG.enabled)
assert settings.DEBUG.enabled is False

print(settings.get("debug.enabled"))
assert settings.get("debug.enabled") is False


DEBUG = settings.get("debug.enabled", False)
print(DEBUG)
assert DEBUG is False
