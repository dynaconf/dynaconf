from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.toml")


assert settings.name == "Bruno"

assert "FOO" not in settings
