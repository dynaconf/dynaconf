from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(
    settings_file="settings.yaml",
    apply_default_on_none=True,
    validators=[
        Validator("NAME", default="Bruno Rocha"),
        Validator("CITY", default="Viana"),
    ],
)

assert settings.NAME == "Bruno Rocha", settings.NAME
assert settings.CITY == "Viana", settings.CITY
