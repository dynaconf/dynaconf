from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=[
        "../settings.toml",
        "../configs/config1.yaml",
        "../configs/config2.yaml",
    ]
)


assert settings.VALUE == 1
assert settings.NAME == "Bruno"
assert settings.LASTNAME == "Rocha"
