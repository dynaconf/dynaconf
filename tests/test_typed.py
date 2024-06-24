import os
from typing import Annotated
from typing import Optional
from typing import Union

import pytest

from dynaconf.typed import DictValue
from dynaconf.typed import Dynaconf
from dynaconf.typed import DynaconfSchemaError
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
    class Plugin(DictValue):
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


def test_annotated_forbidden_with_dictvalue():
    class Plugin(DictValue):
        name: str

    class Settings(Dynaconf):
        # This is not allowed, should add validators on the dictvalue type itself
        plug: Annotated[Plugin, Validator()]

    msg = "DictValue type cannot be Annotated"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_enclosed_forbidden_with_more_than_one_arg():
    class Plugin(DictValue):
        value: list[Union[int, float, bool], int, float]

    class Settings(Dynaconf):
        plug: Plugin

    msg = "Invalid enclosed type for plug.value enclosed types"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_enclosed_type_validates(monkeypatch):
    class Plugin(DictValue):
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
    class Plugin(DictValue):
        name: str

    class Extra(DictValue):
        plugins: list[Plugin]

    class Database(DictValue):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", '@json [{"name": null}]')
        msg = r"database.extra.plugins\[].name must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_deeply_enclosed_type_validates_with_bare_type(monkeypatch):
    class Extra(DictValue):
        plugins: list[str]

    class Database(DictValue):
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

    class Extra(DictValue):
        plugins: list[str]

    class Database(DictValue):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", "@json []")
        assert Settings().database.extra.plugins == []


def test_sub_types_works(monkeypatch):
    class Plugin(DictValue):
        name: str
        path: Optional[
            str
        ]  # NOTE: This must mark path as not required on dict
        order: Union[int, bool, None]  # This is the same as above ^

    class Auth(DictValue):
        username: str
        password: int

    class Extra(DictValue):
        log: bool = True
        socket_type: Annotated[int, Validator(is_in=[1, 2, 3])] = 1
        transactions: bool
        auth: Auth
        plugins: list[Plugin]
        # Make this work
        batatas: list[int] = [1, 2]

    class Database(DictValue):
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
    class Database(DictValue):
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


def test_deeply_dictvalue_fail_validation(monkeypatch):
    """Ensure validation happens on deeply nested type"""

    class Auth(DictValue):
        username: str
        password: int

    class Extra(DictValue):
        log: bool = True
        socket_type: Annotated[int, Validator(is_in=[1, 2, 3])] = 1
        auth: Auth

    class Database(DictValue):
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


##### TYPING SCENARIOS #######


# Use dynaconf_options to set Dynaconf initialization
# NOTE: ADD more options for completeness
def test_dynaconf_options(monkeypatch):
    class Settings(Dynaconf):
        dynaconf_options = Options(envvar_prefix="XPTO")
        name: str

    with monkeypatch.context() as m:
        m.setenv("XPTO_NAME", "Bruno")
        settings = Settings()
        assert settings.name == "Bruno"

    with monkeypatch.context() as m:
        m.setenv("FOO_NAME", "Erik")
        settings = Settings(envvar_prefix="FOO")
        assert settings.name == "Erik"

    settings = Settings(name="Karla")
    assert settings.name == "Karla"


# Set validation as immediate or lazy
def test_eager_validation(monkeypatch):
    class Settings(Dynaconf):
        dynaconf_options = Options(envvar_prefix="XPTO")
        name: Annotated[str, Validator(ne="Valdemort")]

    with monkeypatch.context() as m:
        m.setenv("XPTO_NAME", "Valdemort")
        err_msg = "name must ne Valdemort"
        with pytest.raises(ValidationError, match=err_msg):
            Settings()


def test_lazy_validation(monkeypatch):
    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="XPTO",
            _trigger_validation=False,
        )
        name: Annotated[str, Validator(ne="Valdemort")]

    with monkeypatch.context() as m:
        m.setenv("XPTO_NAME", "Valdemort")
        settings = Settings()
        err_msg = "name must ne Valdemort"
        with pytest.raises(ValidationError, match=err_msg):
            settings.validators.validate()


# Validate type based on annotated type `name: T`
def test_validate_based_on_type_annotation(monkeypatch):
    class Settings(Dynaconf):
        dynaconf_options = Options(envvar_prefix="XPTO")
        name: str

    with monkeypatch.context() as m:
        m.setenv("XPTO_NAME", "1234")
        err_msg = "name must is_type_of .+str"
        with pytest.raises(ValidationError, match=err_msg):
            Settings()


# handle dictvalue subtype
def test_dictvalue_subtype():
    class Person(DictValue):
        name: str = "Bruno"
        age: int

    class Settings(Dynaconf):
        person: Person

    err_msg = "person.age is required"
    with pytest.raises(ValidationError, match=err_msg):
        Settings()


# Set default based `name: T = default`
def test_default_based_on_type_annotation(monkeypatch):
    class Person(DictValue):
        name: str = "Bruno"
        age: int

    class Settings(Dynaconf):
        name: Annotated[str, Validator(ne="Valdemort")] = "John"
        age: int = 45
        colors: list[str] = ["red", "green", "blue"]
        option: Union[int, float, bool] = 4.2
        kwargs: dict[str, int] = {"foo": 3}
        person: Person = Person(age=42)  # works with instance
        # also works with dict overriding Person class defaults
        other_person: Person = {"name": "Erik", "age": 5}
        even_other_person: Person = {}
        yet_another_person: Person

    # arguments passed to init will combine with Person defaults
    settings = Settings(
        even_other_person={"age": 21},
        yet_another_person={"name": "John", "age": 19},
    )

    assert settings.name == "John"
    assert settings.age == 45
    assert settings.colors == ["red", "green", "blue"]
    assert settings.option == 4.2
    assert settings.kwargs.foo == 3
    assert settings.person.name == "Bruno"
    assert settings.person.age == 42
    assert settings.other_person.name == "Erik"
    assert settings.other_person.age == 5
    assert settings.even_other_person.name == "Bruno"
    assert settings.even_other_person.age == 21
    assert settings.yet_another_person.name == "John"
    assert settings.yet_another_person.age == 19


# Extract Validators from Annotated `field: Annotated[T, Validator()]`
def test_extracted_validators(monkeypatch):
    def cast_url(v):
        return v.lower()

    def auth_condition(v):
        return "token" in v

    class Auth(DictValue):
        token: Annotated[str, Validator(len_min=10)]

    class Settings(Dynaconf):
        dynaconf_options = Options(
            _trigger_validation=False,
        )
        name: Annotated[str, Validator(ne="Valdemort")]
        age: int
        team: str = "Default"
        colors: Annotated[list, Validator(cont="red")]
        port: Annotated[int, Validator(lt=1000), Validator(gt=10)]
        url: Annotated[str, Validator(cast=cast_url)]
        auth: Annotated[dict, Validator(condition=auth_condition)]
        typed_auth: Auth

    settings = Settings()

    expected = [
        {
            "names": ("name",),
            "operations": {"ne": "Valdemort", "is_type_of": str},
            "required": True,
        },
        {
            "names": ("age",),
            "operations": {"is_type_of": int},
            "required": True,
        },
        {
            "names": ("team",),
            "operations": {"is_type_of": str},
            "required": False,
        },
        {
            "names": ("colors",),
            "operations": {"is_type_of": list, "cont": "red"},
            "required": True,
        },
        {
            "names": ("port",),
            "operations": {"is_type_of": int, "lt": 1000},
            "required": True,
        },
        {
            "names": ("port",),
            "operations": {"is_type_of": int, "gt": 10},
            "required": True,
        },
        {
            "names": ("url",),
            "operations": {
                "is_type_of": str,
            },
            "cast": cast_url,
            "required": True,
        },
        {
            "names": ("auth",),
            "operations": {"is_type_of": dict},
            "condition": auth_condition,
            "required": True,
        },
        {
            "names": ("typed_auth.token",),
            "operations": {"is_type_of": str, "len_min": 10},
            "required": True,
        },
    ]

    for i, validator in enumerate(settings.validators):
        for key, val in expected[i].items():
            assert getattr(validator, key) == val

    errors = settings.validators.validate_all(raise_error=False)
    for i, exp in enumerate(item for item in expected if item["required"]):
        assert exp["names"][0] in str(errors[i])

    settings = Settings(
        name="Valdemort",
        age=4.1,
        team=True,
        colors={"red": "green"},
        port=5,
        url="SERVER.com",
        auth="user",
        typed_auth={"token": []},
    )
    errors = settings.validators.validate_all(raise_error=False)
    expected_errors = [
        "name must ne Valdemort",
        "age must is_type_of <class 'int'> but it is 4.1",
        "team must is_type_of <class 'str'> but it is True",
        "colors must is_type_of <class 'list'> but it is {'red': 'green'}",
        "port must gt 10 but it is 5",
        "auth invalid for auth_condition(user)",
        "typed_auth.token must len_min 10 but it is []",
    ]
    for i, error in enumerate(errors):
        assert expected_errors[i] in str(error)


# Forbid validators with defaults,is_type_of,names,must_exist,required
@pytest.mark.parametrize(
    "invalid_arg",
    [
        {"required": True},
        {"must_exist": True},
        {"is_type_of": int},
        {"default": 42},
        ("name",),
    ],
    ids=lambda value: str(value),
)
def test_some_arguments_forbid_on_validators(invalid_arg):
    """these arguments doesnt make sense on a typed dynaconf"""
    with pytest.raises(TypeError):
        Validator(**invalid_arg)


# Forbid Annotated with types out of the allowed list
# Forbid args to Annotated that are not Validator `Annotated[T, strange_thing]`
# Handle Union types `field: Union[T, T, T]`
# Handle Optional types `field: Optional[T]` and `field: Union[T, None]`
# Handle list enclosed types `field: list[T]`  (and with default)
# Handle empty list, must be allowed `field: list[T]` accepts `[]`
# Handle list enclosed union `field: list[Union[T, T, T]]`
# Handle list enclosed optional `field: list[Optional[T]]`
# Handle list enclosed new union `field: list[T | T]`
# Forbid list enclosed with more than one arg `list[T, T]`
# Handle Annotated + enclosed type `field: Annotated[list[T], Validator()]`
# Handle Annotated + union type `field: Annotated[Union[T, T], Validator()]`
# Handle Annotated + optional `field: Annotated[Optional[T], Validator()]`
# Handle Annotated + new union `field: Annotated[T | T, Validator()]`
# Handle DictValue `class Struct: ...` - `field: Struct`
# Ensure DictValue adds a is_type_of=dict validator
# Forbid DictValue Subtype on Annotated `Annotated[DictValue, ...]`
# Handle deeply dictvalue Subtype (multiple levels)
# Handle enclosed SubType `field: list[Struct]`
# Handle deeply dictvalue Subtype (multiple levels) with enclosed types
# Forbid enclosed subtype with defaults
# Forbid enclosed subtypes that are not on allowed list `field: list[A]`
# Forbid union subtypes that are not on allowed list `field: list[Union[A]]`
# Handle dict type `field: dict[T, T]` + Annotated and enclosed
# Handle tuple type `field: tuple[T, T, T]` + Annotated and enclosed
# Handle Any type in all cases
# Handle Totality and Allow Extra

##### IDEAS  ###########

# Move typed.py to typed/main.py
# Move helpers to typed/utils.py
# Define ALLOWED_TYPES as type aliases on typed/types.py
