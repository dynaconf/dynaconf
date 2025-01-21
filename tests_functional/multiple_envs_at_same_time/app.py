from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    environments=True,
    settings_files=["defaults.py"],
    env_switcher="BLARG_MODE",
    envvar_prefix="BLARG",
)

PORT = settings.get("PORT", 0)
print(f"{settings.DEBUG=} {settings.HOST=} {PORT=}")
