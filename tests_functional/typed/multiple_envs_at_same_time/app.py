from __future__ import annotations

from dynaconf.typed import Dynaconf
from dynaconf.typed import Options


class Settings(Dynaconf):
    dynaconf_options = Options(
        environments=True,
        settings_files=["defaults.py"],
        env_switcher="BLARG_MODE",
        envvar_prefix="BLARG",
    )


settings = Settings()

PORT = settings.get("PORT", 0)
print(f"{settings.DEBUG=} {settings.HOST=} {PORT=}")
