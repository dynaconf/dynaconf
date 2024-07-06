import os
import sys
from typing import Annotated
from typing import Optional
from typing import Union

import pytest

from dynaconf.typed import DictValue
from dynaconf.typed import Dynaconf
from dynaconf.typed import DynaconfSchemaError
from dynaconf.typed import ItemsValidator
from dynaconf.typed import NotRequired
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


def test_enclosed_type_raises_for_invalid_enclosed():
    class Dummy: ...

    class Settings(Dynaconf):
        plugins: list[Dummy]

    msg = "Invalid type 'Dummy'"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_union_enclosed_type_raises_for_invalid_enclosed():
    class A: ...

    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool, A]]

    msg = "Invalid type 'A'"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


def test_annotated_with_dictvalue():
    class Plugin(DictValue):
        name: Annotated[Union[str, int], Validator()]

    class Settings(Dynaconf):
        # This is not allowed, should add validators on the dictvalue type itself
        plug: Annotated[Plugin, Validator(contains="name")]

    msg = "plug.name must is_type_of.+Union\[str, int]"
    with pytest.raises(ValidationError, match=msg):
        Settings(plug={"name": 4.2})


# NOT SURE ABOUT THIS
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
        msg = r"plugins.0.name must is_type_of"
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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="not supported on 3.9")
def test_new_union_validates(monkeypatch):
    class Settings(Dynaconf):
        number: int | float | bool

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBER", "one")
        msg = r"number must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_validates_type(monkeypatch):
    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool]]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", '["banana"]')
        msg = "numbers must is_type_of list\[typing.Union\[int, float, bool]]"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_validates_operation(monkeypatch):
    class Settings(Dynaconf):
        numbers: Annotated[list[Union[int, float, bool]], Validator(len_min=3)]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", "[1]")
        msg = "numbers must len_min 3"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_validates_items_operations(monkeypatch):
    class Settings(Dynaconf):
        numbers: Annotated[
            list[Union[int, float]], ItemsValidator(Validator(gt=3))
        ]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", "[1]")
        msg = r"numbers.0 must gt 3 but it is 1"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_union_enclosed_type_works(monkeypatch):
    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool]]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", "[1, 4.2, true]")
        settings = Settings()
        assert settings.numbers == [1, 4.2, True]


def test_union_enclosed_type_raises_validation(monkeypatch):
    class Settings(Dynaconf):
        numbers: list[Union[int, float, bool]]

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_NUMBERS", "[1, 4.2, 'Batata']")
        msg = r"\b(numbers.0|must|is_type_of|Union|int|float|bool|Batata)\b"
        with pytest.raises(ValidationError, match=msg):
            Settings()


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
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", '@json [{"name": 42}]')
        msg = r"database.extra.plugins.0.name must is_type_of"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_deeply_enclosed_type_validates_with_bare_dict(monkeypatch):
    class Extra(DictValue):
        plugins: list[dict]

    class Database(DictValue):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", "[1]")
        msg = r"database.extra.plugins must is_type_of list\[dict]"
        with pytest.raises(ValidationError, match=msg):
            Settings()


def test_deeply_enclosed_type_validates_with_parameterized_dict(monkeypatch):
    class Extra(DictValue):
        plugins: list[dict[str, int]]

    class Database(DictValue):
        extra: Extra

    class Settings(Dynaconf):
        database: Database

    with monkeypatch.context() as m:
        m.setenv("DYNACONF_DATABASE__EXTRA__PLUGINS", '@json [{"name": 4.3}]')
        msg = r"database.extra.plugins must is_type_of list\[dict\[str, int]]"
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
        msg = r"database.extra.plugins must is_type_of list\[str]"
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
        # path: NotRequired[str]
        # order: Union[int, bool, None]

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
        database: Database = Database()
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
        auth: Auth = Auth()

    class Database(DictValue):
        host: str = "server.com"
        port: Annotated[int, Validator(gt=999)]
        engine: str = "postgres"
        extra: Extra = Extra()

    class Settings(Dynaconf):
        dynaconf_options = Options(
            envvar_prefix="MYTYPEDAPP",
        )
        database: Database = Database()
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


# Forbid `name: UnsupportedType`
def test_only_supported_types_can_be_used():
    class A: ...

    class Settings(Dynaconf):
        dynaconf_options = Options(_trigger_validation=False)
        name: A

    err_msg = "Invalid type 'A'"
    with pytest.raises(DynaconfSchemaError, match=err_msg):
        Settings()


# handle dictvalue subtype
def test_dictvalue_subtype():
    class Person(DictValue):
        name: str = "Bruno"
        age: int

    class Settings(Dynaconf):
        person: Person = Person()

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
def test_extracted_validators_from_annotated(monkeypatch):
    def cast_url(v):
        return v.lower()

    def auth_condition(v):
        return "token" in v

    class Auth(DictValue):
        token: Annotated[str, Validator(len_min=10)]

    not_banana = Validator(ne="banana")

    class Settings(Dynaconf):
        dynaconf_options = Options(
            _trigger_validation=False,
        )
        name: Annotated[str, Validator(ne="Valdemort")]
        age: int
        team: str = "Default"
        colors: Annotated[list, Validator(contains="red")]
        port: Annotated[int, Validator(lt=1000), Validator(gt=10)]
        url: Annotated[str, Validator(cast=cast_url)]
        auth: Annotated[dict, Validator(condition=auth_condition)]
        typed_auth: Auth
        fruits: Annotated[list[str], ItemsValidator(not_banana)]

    settings = Settings()

    expected = [
        {
            "names": ("name",),
            "operations": {"is_type_of": str},
            "required": True,
        },
        {
            "names": ("name",),
            "operations": {"ne": "Valdemort"},
        },
        {
            "names": ("age",),
            "operations": {"is_type_of": int},
            "required": True,
        },
        {
            "names": ("team",),
            "operations": {"is_type_of": str},
        },
        {
            "names": ("colors",),
            "operations": {"is_type_of": list},
            "required": True,
        },
        {
            "names": ("colors",),
            "operations": {"contains": "red"},
        },
        {
            "names": ("port",),
            "operations": {"is_type_of": int},
            "required": True,
        },
        {
            "names": ("port",),
            "operations": {"lt": 1000},
        },
        {
            "names": ("port",),
            "operations": {"gt": 10},
        },
        {
            "names": ("url",),
            "operations": {"is_type_of": str},
            "required": True,
        },
        {
            "names": ("url",),
            "cast": cast_url,
        },
        {
            "names": ("auth",),
            "operations": {"is_type_of": dict},
            "required": True,
        },
        {
            "names": ("auth",),
            "condition": auth_condition,
        },
        {
            "names": ("typed_auth",),
            "operations": {"is_type_of": Auth},
            "required": True,
        },
        {
            "names": ("fruits",),
            "operations": {"is_type_of": list[str]},
            "required": True,
        },
        {
            "names": ("fruits",),
            "items_validators": [not_banana],
        },
    ]

    for i, validator in enumerate(settings.validators):
        for key, val in expected[i].items():
            attr = getattr(validator, key)
            if key == "operations":
                for item in val.items():
                    assert item in tuple(attr.items())
            else:
                assert attr == val

    errors = settings.validators.validate_all(raise_error=False)
    for i, exp in enumerate(item for item in expected if item.get("required")):
        assert exp["names"][0] in str(errors[i])

    settings = Settings(
        name="Valdemort",
        age=4.1,
        team=True,
        colors={"red": "green"},
        port=5,
        url="SERVER.com",
        auth={"username": "foo"},
        typed_auth={"token": []},
        fruits=["apple", "banana"],
    )
    errors = settings.validators.validate_all(raise_error=False)
    expected_errors = [
        "name must ne Valdemort",
        "age must is_type_of <class 'int'> but it is 4.1",
        "team must is_type_of <class 'str'> but it is True",
        "colors must is_type_of <class 'list'> but it is {'red': 'green'}",
        "port must gt 10 but it is 5",
        "auth invalid for auth_condition({'username': 'foo'})",
        "typed_auth.token must is_type_of <class 'str'> but it is []",
        "fruits.1 must ne banana",
        "typed_auth.token must len_min 10",
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
def test_annotated_accepts_only_supported_types():
    class A: ...

    class Settings(Dynaconf):
        name: Annotated[A, Validator()]

    msg = "Invalid type 'A'"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings(name=A())

    class Settings(Dynaconf):
        name: Annotated[complex, Validator()]

    msg = "Invalid type 'complex'"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


# Forbid args to Annotated that are not Validator `Annotated[T, strange_thing]`
def test_annotated_args_must_be_only_validators():
    # OK
    class Settings(Dynaconf):
        name: Annotated[str, Validator()] = "John"

    Settings()

    # NOT OK
    class Settings(Dynaconf):
        name: Annotated[str, Validator(), "Hello", 123] = "John"

    msg = "Invalid Annotated Args"
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


# Handle Union types `field: Union[T, T, T]`
def test_all_kinds_of_union():
    class Person(DictValue):
        name: str

    class Settings(Dynaconf):
        person: Union[Person, str, dict]

    assert Settings(person="Bruno").person == "Bruno"
    assert Settings(person={"name": "Bruno"}).person.name == "Bruno"
    assert Settings(person=Person()).person == {}
    assert Settings(person=Person(name="Bruno")).person.name == "Bruno"

    with pytest.raises(ValidationError, match="person must is_type_of"):
        Settings(person=1)


# Handle Optional types `field: Optional[T]` and `field: Union[T, None]`
def test_optional_types():
    """Optional and Union[T, None] must define a None default"""

    class Profile(DictValue):
        username: str

    # Good
    class Settings(Dynaconf):
        name: Optional[str] = None
        age: Optional[int] = None
        colors: Optional[list] = None
        profile: Optional[Profile] = None
        city: Union[str, None] = None
        team: Annotated[Optional[str], Validator()] = None
        work: NotRequired[dict]

    Settings(work={}, team="A")

    # Not Good
    class Settings(Dynaconf):
        name: Optional[str]  # Should have used NotRequired

    msg = "Optional Union must assign `None` explicitly as default."
    with pytest.raises(DynaconfSchemaError, match=msg):
        Settings()


# Handle NotRequired
def test_notrequired():
    class Settings(Dynaconf):
        name: NotRequired[str]
        name2: Annotated[NotRequired[str], Validator()]
        name3: NotRequired[Annotated[str, Validator()]]  # same as above

    # No error as none of the variables are required
    settings = Settings()

    # However the NotRequired attribute might be undefined
    with pytest.raises(AttributeError):
        settings.name

    # Same on SubTypes
    class Person(DictValue):
        name: str
        age: NotRequired[int]
        team: NotRequired[Annotated[str, Validator(is_in=["A", "B"])]]

    class Settings(Dynaconf):
        person: Person
        person2: NotRequired[Person]
        something: NotRequired[list]

    # Good, partial dict because some fields are NotRequired
    Settings(person={"name": "Bruno"})

    # Validates for types and checks if a not required field is informed
    with pytest.raises(
        ValidationError,
        match="person.age must is_type_of.+int",
    ):
        Settings(person={"name": "Bruno", "age": "too-old"})

    with pytest.raises(
        ValidationError, match="person.team must is_in \['A', 'B']"
    ):
        Settings(person={"name": "Bruno", "team": "C"})

    with pytest.raises(
        ValidationError,
        match="something must is_type_of.+list",
    ):
        Settings(person={"name": "Bruno", "team": "A"}, something=5.6)


# Handle list enclosed types `field: list[T]`  (and with default)
# Handle empty list, must be allowed `field: list[T]` accepts `[]`
def test_list_enclosed_type_is_required():
    # simple and required
    class Settings(Dynaconf):
        colors: list[str]

    Settings(colors=[])
    Settings(colors=["a"])

    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors is required",
    ):
        Settings()


# Forbid list enclosed with more than one arg `list[T, T]`
@pytest.mark.xfail
def test_list_enclosed_type_with_multi_args():
    ...

    # simple and required with multi args
    # I THINK WE MUST ADD SUPPORT FOR IT
    # but now it raises error
    class Settings(Dynaconf):
        colors: list[str, float]

    Settings(colors=[])
    Settings(colors=["a"])
    Settings(colors=[4.2])

    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors is required",
    ):
        Settings()


# Handle list enclosed union `field: list[Union[T, T, T]]`
def test_list_enclosed_type_with_union():
    # Unionized and required
    class Settings(Dynaconf):
        colors: list[Union[str, int]]

    Settings(colors=[])
    Settings(colors=["a"])
    Settings(colors=[1])

    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors is required",
    ):
        Settings()


def test_list_enclosed_type_outer_union():
    """
    As an alternative to list[T, T] one can use
    Union[list[T], list[T]]
    """

    # Outer Unionized and required
    class Settings(Dynaconf):
        colors: Union[list[str], str]

    Settings(colors=[])
    Settings(colors=["a"])
    Settings(colors="a")

    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors is required",
    ):
        Settings()


def test_list_enclosed_type_annotated():
    # Annotated with Validator
    class Settings(Dynaconf):
        dynaconf_options = Options(_trigger_validation=False)
        colors: Annotated[list[str], Validator(contains="red")]

    Settings(colors=["red"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1).validators.validate()
    with pytest.raises(
        ValidationError,
        match="Invalid Operation 'contains' for type <class 'int'> on 'colors'",
    ):
        Settings(colors=1).validators.validate_all()
    with pytest.raises(
        ValidationError,
        match="colors must contains red",
    ):
        Settings(colors=[]).validators.validate()


def test_list_enclosed_type_annotated_with_union():
    # Annotated and Unionized
    class Settings(Dynaconf):
        colors: Annotated[Union[list[str], str], Validator(contains="blue")]

    Settings(colors=["blue"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors must contains blue",
    ):
        Settings(colors=[])


@pytest.mark.skipif(sys.version_info < (3, 10), reason="not supported on 3.9")
def test_list_enclosed_type_annotated_with_new_union():
    # Annotated and Unionized
    class Settings(Dynaconf):
        colors: Annotated[list[str] | str, Validator(contains="blue")]

    Settings(colors=["blue"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors must contains blue",
    ):
        Settings(colors=[])


def test_list_enclosed_type_annotated_with_union_nested():
    # Annotated and Unionized with Nesting Union (python will flatten it)
    class Settings(Dynaconf):
        colors: Annotated[
            Union[list[Union[str, int]], str], Validator(contains="green")
        ]

    Settings(colors=["green"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=1)
    with pytest.raises(
        ValidationError,
        match="colors must contains green",
    ):
        Settings(colors=[])


def test_list_enclosed_type_with_more_complex_unions():
    # More combinations with Unions
    class Settings(Dynaconf):
        colors: Annotated[
            Union[list[Union[str, int]], str, Union[str, int]],
            Validator(contains="purple"),
        ]

    Settings(colors=["purple"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=4.2)
    with pytest.raises(
        ValidationError,
        match="colors must contains purple",
    ):
        Settings(colors=[])


def test_list_enclosed_type_crazy_type():
    # A type that makes no sense but still validates
    crazy_type = Union[
        list[Union[str, int]], str, Union[list[str], tuple[Union[int, float]]]
    ]

    class Settings(Dynaconf):
        colors: Annotated[crazy_type, Validator(contains="pink")]

    Settings(colors=["pink"])
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list",
    ):
        Settings(colors=4.2)
    with pytest.raises(
        ValidationError,
        match="colors must contains pink",
    ):
        Settings(colors=[])


def test_list_enclosed_type_annotated_notrequired():
    # NotRequired
    class Settings(Dynaconf):
        colors: Annotated[NotRequired[list[str]], Validator(contains="yellow")]

    Settings()
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list\[str]",
    ):
        Settings(colors=[1, 2, 3])
    with pytest.raises(
        ValidationError,
        match="colors must contains yellow",
    ):
        Settings(colors=["red"])


def test_list_enclosed_type_notrequired():
    # NotRequired
    class Settings(Dynaconf):
        colors: NotRequired[list[str]]

    Settings()
    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+list\[str]",
    ):
        Settings(colors=[1, 2, 3])


def test_list_enclosed_type_with_default():
    # With Default Value
    crazy_type = Union[
        list[Union[str, int]], str, Union[list[str], tuple[Union[int, float]]]
    ]

    class Settings(Dynaconf):
        colors: Annotated[crazy_type, Validator(contains="cyan")] = ["cyan", 1]

    assert Settings().colors == ["cyan", 1]


# Handle list enclosed optional `field: list[Optional[T]]`
def test_list_enclosed_type_with_optional():
    class Settings(Dynaconf):
        colors: list[Optional[str]]  # Means list can be [], [None], [str]

    Settings(colors=[])
    Settings(colors=[None, None])
    Settings(colors=["red"])
    with pytest.raises(
        ValidationError,
        match="colors is required",
    ):
        Settings()

    with pytest.raises(
        ValidationError,
        match="colors must is_type_of.+Optional\[str]",
    ):
        Settings(colors=["red", "#123", 3])


def test_usage_of_dict_value():
    class Service(DictValue):
        name: str

    class Kind(DictValue):
        id: int
        services: list[Service]

    class Profile(DictValue):
        username: str
        group: int = 1
        team: int = 42
        kind: Kind

    class Person(DictValue):
        name: str = "batata"
        active: bool
        bla: NotRequired[float]
        numbers: list[int]
        age: Annotated[NotRequired[int], Validator(gt=90)]
        profile: Profile = Profile()  # w/ defaults
        # profile2: Profile  # No defaults
        profile2: NotRequired[Profile]
        code: Union[str, int, float]

    bruno = Person(
        name="Bruno",
        code="XPTO",
        numbers=[1, 2, 3],
        active=False,
        profile=Profile(
            username="br", kind=Kind(id=9, services=[Service(name="A")])
        ),
    )
    jj = Person(
        name="jj",
        code=1234,
        numbers=[1, 7, 9],
        active=True,
        profile=Profile(
            username="j", kind=Kind(id=3, services=[Service(name="B")])
        ),
    )
    boss = Person(
        name="Mike",
        code=45.5,
        numbers=[5, 6, 7],
        active=False,
        profile=Profile(
            username="m", kind=Kind(id=56, services=[Service(name="C")])
        ),
    )

    class Settings(Dynaconf):
        dynaconf_options = Options(_trigger_validation=False)
        # not covered
        # thing: Union[int, str]
        # person_union: Union[Person, str, None]
        # people_optional: Optional[list[Person]] = None
        # people_notrequired: NotRequired[list[Person]]
        # team: Annotated[list[Person], Validator(len_min=1)]

        # covered
        number: int = 99
        person: Person = {"profile": {"username": "aaa", "group": 2}}
        contact: Annotated[Person, Validator(contains="name")]
        person_optional: Optional[Person] = None
        person_default: Person = Person(
            name="Person With Defaults",
            numbers=[3, 4],
            code=5678,
            active=False,
            profile=Profile(
                username="aa",
                kind=Kind(
                    id=9,
                    services=[
                        Service(name="A"),
                        Service(name="B"),
                    ],
                ),
            ),
        )
        person_notrequired: NotRequired[Person]
        people: list[Person]
        people_default: list[Person] = [jj, boss]

    settings = Settings(
        _debug_mode=True,
        person=bruno,
        other_number=14,
        number="@get other_number",
        contact=jj,
        people=[bruno, jj, boss],
        # team=[boss],
        # person_optional={"name": 1},  # must raise type error
        # person_notrequired={"name": 2},  # must raise type error
        # person_notrequired={"name": "aaaa"},  # must raise type error
    )

    settings.validators.validate()

    assert settings.number == 14
    assert settings.person.name == "Bruno"
    assert settings.person.profile.kind.services[0].name == "A"
    assert settings.people[1].name == "jj"


# Handle deeply dictvalue Subtype (multiple levels) with enclosed types
# Handle tuple type `field: tuple[T, T, T]` + Annotated and enclosed
# Handle Any type in all cases
# Handle Totality and Allow Extra

##### IDEAS  ###########

# Move typed.py to typed/main.py
# Move helpers to typed/utils.py
# Define ALLOWED_TYPES as type aliases on typed/types.py
