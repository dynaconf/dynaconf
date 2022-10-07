from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ISSUE728",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
)
