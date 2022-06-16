from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="setting.py")

assert settings.FOO == "BAR"
assert settings.BAR == "zaz"
