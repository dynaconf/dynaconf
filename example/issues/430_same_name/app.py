from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file=["settings.yaml", "folder/settings.yaml"], merge_enabled=True
)

assert settings.FOO.bar == 1
assert settings.FOO.zaz == 2
