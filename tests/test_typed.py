import os
from typing import Annotated
from typing import Optional
from typing import Union

import pytest

from dynaconf.typed import Dynaconf
from dynaconf.typed import DynaconfSchemaError
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

    # Don't trigger validation immediately
    settings = Settings(host="denied.com")

    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_validator_from_types():
    class Settings(Dynaconf):
        host: str = "server.com"
        port: int

    with pytest.raises(ValidationError, match="port is required"):
        Settings()


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


def test_enclosed_type_raises_for_defaults():
    class Plugin(Nested):
        name: str = "default_name"

    class Settings(Dynaconf):
        plugins: list[Plugin]

    msg = "List enclosed types cannot define default values"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_enclosed_type_raises_for_invalid_enclosed():
    class Dummy: ...

    class Settings(Dynaconf):
        plugins: list[Dummy]

    msg = "Invalid enclosed type"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_union_enclosed_type_raises_for_invalid_enclosed():
    class A: ...

    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool, A]]

    msg = "Invalid enclosed type 'A'"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_annotated_forbidden_with_nested():
    class Plugin(Nested):
        name: str

    class Settings(Dynaconf):
        # This is not allowed, should add validators on the nested type itself
        plug: Annotated[Plugin, Validator()]

    msg = "Nested type cannot be Annotated"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_enclosed_forbidden_with_more_than_one_arg():
    class Plugin(Nested):
        value: list[Union[int, float, bool], int, float]

    class Settings(Dynaconf):
        plug: Plugin

    msg = "Invalid enclosed type for plug.value enclosed types"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_enclosed_type_validates(monkeypatch):
    class Plugin(Nested):
        name: str

    class Settings(Dynaconf):
        plugins: list[Plugin]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_PLUGINS", '@json [{"name": true}]')
        msg = r"plugins\[].name must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_type_validates(monkeypatch):
    class Settings(Dynaconf):
        number: Union[int, float, bool]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBER", "one")
        msg = r"number must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_validates(monkeypatch):
    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool]]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", '["banana"]')
        msg = r"numbers\[] must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_works(monkeypatch):
    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool]]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", "[1, 4.2, true]")
        settings = Settings()
        assert settings.numbers == [1, 4.2, True]


def test_deeply_enclosed_type_validates(monkeypatch):
    class Plugin(Nested):
        name: str

    class Extra(Nested):
        plugins: list[Plugin]

    class Database(Nested):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", '@json [{"name": null}]')
        msg = r"database.extra.plugins\[].name must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_deeply_enclosed_type_validates_with_bare_type(monkeypatch):
    class Extra(Nested):
        plugins: list[str]

    class Database(Nested):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", "@json [12]")
        msg = r"database.extra.plugins\[] must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_deeply_enclosed_type_validates_with_bare_type_allows_empty(
    monkeypatch,
):
    """Ensure empty list is valid when list has enclosed type.

    list[T] will validate [T] but also an empty list []
    NOTE: It does not look right for me, but looks like it is valid.
    https://mypy-play.net/?gist=d16da1574497dbe585eab679f09432ef
    """

    class Extra(Nested):
        plugins: list[str]

    class Database(Nested):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", "@json []")
        assert Settings().database.extra.plugins == []


def test_sub_types_works(monkeypatch):
    class Plugin(Nested):
        name: str
        path: Optional[
            str
        ]  # NOTE: This must mark path as not required on dict
        order: Union[int, bool, None]  # This is the same as above ^

    class Auth(Nested):
        username: str
        password: int

    class Extra(Nested):
        log: bool = True
        socket_type: Annotated[int, Validator(is_in=[1, 2, 3])] = 1
        transactions: bool
        auth: Auth
        plugins: list[Plugin]
        # Make this work
        batatas: list[int] = [1, 2]

    class Database(Nested):
        host: str = "server.com"
        port: Annotated[int, Validator(gt=999)]
        engine: str = "postgres"
        extra: Extra

    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="MYTYPEDAPP",
        )
        version: Union[int, float, bool]
        database: Database
        batata: Annotated[int, Validator(gt=999)]

    with monkeypatch.context() as m:
        m.setenv("MYTYPEDAPP_version", "4.4")
        m.setenv("MYTYPEDAPP_BATATA", "1000")
        m.setenv("MYTYPEDAPP_DATABASE__PORT", "5000")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__TRANSACTIONS", "true")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__AUTH__USERNAME", "admin")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__AUTH__PASSWORD", "1234")
        m.setenv("MYTYPEDAPP_database__extra__plugins___0__name", "MyPlugin")
        m.setenv("MYTYPEDAPP_database__extra__plugins___0__order", "1")
        # NOTE: This key is not in the Plugin spec, must be disallowed
        # and raise validation
        m.setenv("MYTYPEDAPP_database__extra__plugins___0__batata", "1")

        settings = Settings()
        assert settings.database.port == 5000
        assert settings.database.host == "server.com"
        assert settings.database.engine == "postgres"
        assert isinstance(settings.database.extra.plugins[0]["name"], str)


def test_sub_types_fail_validation(monkeypatch):
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

    with monkeypatch.context() as m:
        m.setenv("MYTYPEDAPP_DATABASE__PORT", "5000")
        os.environ["MYTYPEDAPP_DATABASE__PORT"] = "888"

        error_msg = "database.port must gt 999 but it is 888"
        with pytest.raises(ValidationError, match=error_msg):
            Settings()


def test_deeply_nested_fail_validation(monkeypatch):
    """Ensure validation happens on deeply nested type"""

    class Auth(Nested):
        username: str
        password: int

    class Extra(Nested):
        log: bool = True
        socket_type: Annotated[int, Validator(is_in=[1, 2, 3])] = 1
        auth: Auth

    class Database(Nested):
        host: str = "server.com"
        port: Annotated[int, Validator(gt=999)]
        engine: str = "postgres"
        extra: Extra

    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="MYTYPEDAPP",
        )
        database: Database
        batata: Annotated[int, Validator(gt=999)]

    with monkeypatch.context() as m:
        m.setenv("MYTYPEDAPP_DATABASE__PORT", "5000")
        os.environ["MYTYPEDAPP_DATABASE__PORT"] = "1000"

        error_msg = "database.extra.auth.username is required"
        with pytest.raises(ValidationError, match=error_msg):
            Settings()
