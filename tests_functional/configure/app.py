from __future__ import annotations

from dynaconf import settings

settings.configure(settings_module="/tmp/configure_test/settings.py")

assert settings.MESSAGE == "Hello from tmp"
print(settings.MESSAGE)  # noqa
