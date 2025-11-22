from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    environment=True,  # should be environments but it is an alias
    settings_files="settings.toml",  # should be settings_file it is an alias
)


assert settings.NAME == "Bruno"


settings = Dynaconf(
    ENVIRONMENT=True,  # should be environments but it is an alias
    SETTINGS_FILES="settings.toml",  # should be settings_file it is an alias
)


assert settings.NAME == "Bruno"
