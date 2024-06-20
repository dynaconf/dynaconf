import os
from typing import Annotated

# from typing import Optional
# from typing import Union
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


def test_sub_types_works(monkeypatch):
    class Plugin(Nested):
        name: str  # = "default_name"
        # path: Optional[str]  # NOTE: This must mark path as not required
        # order: int

    class Auth(Nested):
        username: str
        password: int

    class Extra(Nested):
        log: bool = True
        socket_type: Annotated[int, Validator(is_in=[1, 2, 3])] = 1
        transactions: bool
        auth: Auth
        plugins: list[Plugin]

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
        m.setenv("MYTYPEDAPP_BATATA", "1000")
        m.setenv("MYTYPEDAPP_DATABASE__PORT", "5000")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__TRANSACTIONS", "true")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__AUTH__USERNAME", "admin")
        m.setenv("MYTYPEDAPP_DATABASE__EXTRA__AUTH__PASSWORD", "1234")
        m.setenv(
            "MYTYPEDAPP_DATABASE__EXTRA__PLUGINS", '@json [{"name": "xpto"}]'
        )

        settings = Settings()

        assert settings.database.port == 5000
        assert settings.database.host == "server.com"
        assert settings.database.engine == "postgres"


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
