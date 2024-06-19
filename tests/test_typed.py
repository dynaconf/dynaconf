from __future__ import annotations

from typing import Annotated

import pytest

from dynaconf.typed import Dynaconf
from dynaconf.typed import Options
from dynaconf.typed import ValidationError
from dynaconf.typed import Validator


def test_immediate_validation():
    class Settings(Dynaconf):
        host: Annotated[str, Validator(ne="denied.com")]

    with pytest.raises(ValidationError):
        Settings(host="denied.com")


def test_lazy_validation_with_options():
    class Settings(Dynaconf):
        dynaconf_options = Options(_trigger_validation=False)
        host: Annotated[str, Validator(ne="denied.com")]

    # Dont trigger validation immediately
    settings = Settings(host="denied.com")

    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_validator_from_types():
    class Settings(Dynaconf):
        host: str = "server.com"
        port: int

    with pytest.raises(ValidationError) as exc:
        Settings()

    assert "port is required" in str(exc)


def test_default_value_from_types():
    class Settings(Dynaconf):
        host: str = "batata.com"
        port: int = 999

    settings = Settings()
    assert settings.host == "batata.com"
    assert settings.PORT == 999


def test_options_contains_only_valid_and_set_attributes():
    options = Options(
        env="dev",
        envvar_prefix="BATATA",
        settings_file="foo.json",
        _trigger_validation=False,  # not included
    )
    options_dict = options.as_dict()
    assert options_dict == {
        "env": "dev",
        "envvar_prefix": "BATATA",
        "settings_file": "foo.json",
    }
