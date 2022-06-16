from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import ValidationError
from dynaconf import Validator

settings = Dynaconf(settings_file="settings_file.yaml")

settings.validators.register(
    (
        Validator("EXAMPLE.username", must_exist=True)
        & Validator("EXAMPLE.password", must_exist=True)
    )
    | Validator("EXAMPLE.token", must_exist=True)
)

try:
    settings.validators.validate()
except ValidationError as err:
    assert (
        str(err)
        == "combined validators failed EXAMPLE.username is required in env"
        " main and EXAMPLE.password is required in env main or EXAMPLE.token"
        " is required in env main"
    ), str(err)


settings = Dynaconf(settings_file="settings_file.yaml")

settings.validators.register(
    (
        Validator("EXAMPLE.username", must_exist=True)
        | Validator("EXAMPLE.password", must_exist=True)
    )
    | Validator("EXAMPLE.token", must_exist=True)
)

try:
    settings.validators.validate()
except ValidationError as err:
    assert (
        str(err)
        == "combined validators failed EXAMPLE.username is required in env"
        " main or EXAMPLE.password is required in env main or EXAMPLE.token is"
        " required in env main"
    ), str(err)
