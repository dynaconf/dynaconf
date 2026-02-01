from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="module/config/settings.toml",
    environments=True,
)


print(settings.WORKS)  # noqa


assert getattr(settings, "WORKS") == "-m_case"
