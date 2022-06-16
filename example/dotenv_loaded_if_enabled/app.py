from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.toml", load_dotenv=True)


assert settings.name == "Bruno"

assert "FOO" in settings

assert settings.foo == "NAR"
