from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(environments=True, settings_file="settings.toml")
