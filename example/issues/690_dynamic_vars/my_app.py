from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYAPP",
    core_loaders=["YAML"],
    settings_file="my_settings.yaml",
)
