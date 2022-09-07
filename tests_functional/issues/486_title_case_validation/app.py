from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(
    settings_file=[Path(__file__).parent.joinpath("settings.yaml")]
)

print(f"Host: {settings.DATABASE.HOST}")
settings.validators.register(Validator("DATABASE.HOST", must_exist=True))
settings.validators.validate()

print(f"Name: {settings.Operator.Name}")
settings.validators.register(Validator("Operator.Name", must_exist=True))
settings.validators.validate()
