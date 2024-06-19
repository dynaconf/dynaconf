# from __future__ import annotations  # WARNING: remove this when debugging

import os
from typing import Annotated

import pytest

from dynaconf.typed import Dynaconf
from dynaconf.typed import Nested
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


def test_sub_types():
    class Database(Nested):
        host: str = "server.com"
        port: Annotated[int, Validator(gt=999)]
        engine: str = "postgres"

    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="MYTYPEDAPP",
            # _trigger_validation=False,
        )
        database: Database
        batata: Annotated[int, Validator(gt=999)]

    os.environ["MYTYPEDAPP_BATATA"] = "1000"
    os.environ["MYTYPEDAPP_DATABASE__PORT"] = "5000"
    settings = Settings()

    assert settings.database.port == 5000
    assert settings.database.host == "server.com"
    assert settings.database.engine == "postgres"


def test_sub_types_fail_validation():
    class Database(Nested):
        host: str = "server.com"
        port: Annotated[int, Validator(gt=999)]
        engine: str = "postgres"

    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="MYTYPEDAPP",
        )
        database: Database
        batata: Annotated[int, Validator(gt=999)]

    os.environ["MYTYPEDAPP_DATABASE__PORT"] = "888"

    with pytest.raises(ValidationError) as exc:
        Settings()

    assert "database.port must gt 999 but it is 888" in str(exc)
