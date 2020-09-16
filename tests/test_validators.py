from types import MappingProxyType

import pytest

from dynaconf import LazySettings
from dynaconf import ValidationError
from dynaconf import Validator


TOML = """
[default]
EXAMPLE = true
MYSQL_HOST = 'localhost'
DEV_SERVERS = ['127.0.0.1', 'localhost', 'development.com']
VERSION = 1
AGE = 15
NAME = 'BRUNO'
PORT = 8001
BASE_IMAGE = 'bla'
PRESIDENT = 'Lula'
PROJECT = 'hello_world'
SALARY = 2000
WORKS = 'validator'
ZERO = 0
FALSE = false

[development]
MYSQL_HOST = 'development.com'
VERSION = 1
AGE = 15
NAME = 'MIKE'
IMAGE_1 = 'aaa'
IMAGE_2 = 'bbb'
IMAGE_4 = 'a'
IMAGE_5 = 'b'

[production]
MYSQL_HOST = 'production.com'
VERSION = 1
AGE = 15
NAME = 'MIKE'
IMAGE_4 = 'a'
IMAGE_5 = 'b'

[global]
MYSQL_PASSWD = "SuperSecret"
TESTVALUE = "value"
"""


def test_validators_on_init(tmpdir):
    TOML = """
    [default]
    hostname = 'devserver.com'
    username = 'admin'
    """
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True,
        settings_file=str(tmpfile),
        validators=(
            Validator("hostname", eq="devserver.com"),
            Validator("username", ne="admin"),
        ),
    )

    with pytest.raises(ValidationError):
        settings.HOSTNAME


def test_validators_register(tmpdir):

    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="EXAMPLE",
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
        silent=True,
    )
    settings.validators.register(
        Validator("VERSION", "AGE", "NAME", must_exist=True),
        Validator("AGE", lte=30, gte=10),
        Validator("PROJECT", eq="hello_world"),
        Validator("PRESIDENT", env="DEVELOPMENT", ne="Trump"),
        Validator("SALARY", lt=1000000, gt=1000),
        Validator("DEV_SERVERS", must_exist=True, is_type_of=(list, tuple)),
        Validator("MYSQL_HOST", env="DEVELOPMENT", is_in=settings.DEV_SERVERS),
        Validator(
            "MYSQL_HOST", env="PRODUCTION", is_not_in=settings.DEV_SERVERS
        ),
        Validator("NAME", condition=lambda x: x in ("BRUNO", "MIKE")),
        Validator(
            "IMAGE_1",
            "IMAGE_2",
            env="development",
            must_exist=True,
            when=Validator(
                "BASE_IMAGE", must_exist=True, env=settings.ENV_FOR_DYNACONF
            ),
        ),
        Validator(
            "IMAGE_4",
            "IMAGE_5",
            env=("development", "production"),
            must_exist=True,
            when=Validator(
                "BASE_IMAGE", must_exist=False, env=settings.ENV_FOR_DYNACONF
            ),
        ),
        Validator(
            "PORT",
            must_exist=True,
            ne=8000,
            when=Validator("MYSQL_HOST", eq="localhost"),
        ),
        #
        Validator("ZERO", is_type_of=int, eq=0),
        Validator("FALSE", is_type_of=bool, eq=False),
        Validator("NAME", len_min=3, len_max=125),
        Validator("DEV_SERVERS", cont="localhost"),
        Validator("PORT", condition=lambda value: len(str(value)) == 4),
        Validator("PROJECT", len_ne=0),
    )

    assert settings.validators.validate() is None

    settings.validators.register(
        Validator("TESTVALUEZZ", env="development"),
        Validator("TESTVALUE", eq="hello_world"),
    )

    with pytest.raises(ValidationError):
        settings.validators.validate()

    with pytest.raises(TypeError):
        Validator("A", condition=1)

    with pytest.raises(TypeError):
        Validator("A", when=1)


def test_dotted_validators(settings):

    settings.set(
        "PARAMS",
        {"PASSWORD": "secret", "SSL": {"CONTEXT": "SECURE", "ENABLED": True}},
    )

    settings.validators.register(
        Validator("PARAMS", must_exist=True, is_type_of=dict),
        Validator("PARAMS.PASSWORD", must_exist=True, is_type_of=str),
        Validator("PARAMS.SSL", must_exist=True, is_type_of=dict),
        Validator("PARAMS.SSL.ENABLED", must_exist=True, is_type_of=bool),
        Validator("PARAMS.NONEXISTENT", must_exist=False, is_type_of=str),
    )

    assert settings.validators.validate() is None


@pytest.mark.parametrize(
    "validator_instance",
    [
        Validator("TESTVALUE", eq="hello_world"),
        Validator("PROJECT", condition=lambda x: False, env="development"),
        Validator("TESTVALUEZZ", must_exist=True),
        Validator("TESTVALUEZZ", "PROJECT", must_exist=False),
    ],
)
def test_validation_error(validator_instance, tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="EXAMPLE",
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
        silent=True,
    )
    settings.validators.register(validator_instance)
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_no_reload_on_single_env(tmpdir, mocker):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    same_env_validator = Validator(
        "VERSION", is_type_of=int, env="development"
    )
    other_env_validator = Validator("NAME", must_exist=True, env="production")

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="DEVELOPMENt",
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
    )
    using_env = mocker.patch.object(settings, "from_env")

    settings.validators.register(same_env_validator)
    settings.validators.validate()
    using_env.assert_not_called()

    settings.validators.register(other_env_validator)
    settings.validators.validate()
    using_env.assert_any_call("production")
    assert using_env.call_count == 1


@pytest.mark.parametrize(
    "this_validator,another_validator",
    [
        (
            Validator("VERSION", "AGE", "NAME", must_exist=True),
            Validator("VERSION", "AGE", "NAME", must_exist=True),
        ),
        (
            Validator("VERSION") | Validator("AGE"),
            Validator("VERSION") | Validator("AGE"),
        ),
        (
            Validator("VERSION") & Validator("AGE"),
            Validator("VERSION") & Validator("AGE"),
        ),
    ],
)
def test_equality(this_validator, another_validator):
    assert this_validator == another_validator
    assert this_validator is not another_validator


@pytest.mark.parametrize(
    "this_validator,another_validator",
    [
        (
            Validator(
                "IMAGE_1", when=Validator("BASE_IMAGE", must_exist=True)
            ),
            Validator(
                "IMAGE_1", when=Validator("MYSQL_HOST", must_exist=True)
            ),
        ),
        (Validator("VERSION"), Validator("VERSION") & Validator("AGE")),
        (Validator("VERSION"), Validator("VERSION") | Validator("AGE")),
        (
            Validator("VERSION") | Validator("AGE"),
            Validator("VERSION") & Validator("AGE"),
        ),
        (
            Validator("VERSION") | Validator("AGE"),
            Validator("NAME") | Validator("BASE_IMAGE"),
        ),
    ],
)
def test_inequality(this_validator, another_validator):
    assert this_validator != another_validator


def test_ignoring_duplicate_validators(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="EXAMPLE",
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
        silent=True,
    )

    validator1 = Validator("VERSION", "AGE", "NAME", must_exist=True)
    settings.validators.register(
        validator1, Validator("VERSION", "AGE", "NAME", must_exist=True)
    )

    assert len(settings.validators) == 1

    settings.validators.register(validator1)

    assert len(settings.validators) == 1


def test_validator_equality_by_identity():
    validator1 = Validator("FOO", must_exist=True)
    validator2 = validator1
    assert validator1 == validator2


def test_validator_custom_message(tmpdir):
    """Assert custom message is being processed by validator."""
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )

    custom_msg = "You cannot set {name} to {value} in env {env}"
    settings.validators.register(
        Validator("MYSQL_HOST", eq="development.com", env="DEVELOPMENT"),
        Validator("MYSQL_HOST", ne="development.com", env="PRODUCTION"),
        Validator("VERSION", ne=1, messages={"operations": custom_msg}),
    )

    with pytest.raises(ValidationError) as error:
        settings.validators.validate()

    assert custom_msg.format(
        name="VERSION", value="1", env="DEVELOPMENT"
    ) in str(error)


def test_validator_subclass_messages(tmpdir):
    """Assert message can be customized via class attributes"""
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )

    class MyValidator(Validator):
        default_messages = MappingProxyType(
            {
                "must_exist_true": "{name} should exist in {env}",
                "must_exist_false": "{name} CANNOT BE THERE IN {env}",
                "condition": (
                    "{name} BROKE THE {function}({value}) IN env {env}"
                ),
                "operations": (
                    "{name} SHOULD BE {operation} {op_value} "
                    "BUT YOU HAVE {value} IN ENV {env}, PAY ATTENTION!"
                ),
            }
        )

    with pytest.raises(ValidationError) as error_custom_message:
        custom_msg = "You cannot set {name} to {value} in env {env}"
        MyValidator(
            "VERSION", ne=1, messages={"operations": custom_msg}
        ).validate(settings)

    assert custom_msg.format(
        name="VERSION", value="1", env="DEVELOPMENT"
    ) in str(error_custom_message)

    with pytest.raises(ValidationError) as error_operations:
        MyValidator("VERSION", ne=1).validate(settings)

    assert (
        "VERSION SHOULD BE ne 1 "
        "BUT YOU HAVE 1 IN ENV DEVELOPMENT, "
        "PAY ATTENTION!"
    ) in str(error_operations)

    with pytest.raises(ValidationError) as error_conditions:
        MyValidator("VERSION", condition=lambda value: False).validate(
            settings
        )

    assert ("VERSION BROKE THE <lambda>(1) IN env DEVELOPMENT") in str(
        error_conditions
    )

    with pytest.raises(ValidationError) as error_must_exist_false:
        MyValidator("VERSION", must_exist=False).validate(settings)

    assert ("VERSION CANNOT BE THERE IN DEVELOPMENT") in str(
        error_must_exist_false
    )

    with pytest.raises(ValidationError) as error_must_exist_true:
        MyValidator("BLARGVARGST_DONT_EXIST", must_exist=True).validate(
            settings
        )

    assert ("BLARGVARGST_DONT_EXIST should exist in DEVELOPMENT") in str(
        error_must_exist_true
    )


def test_positive_combined_validators(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)
    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )
    settings.validators.register(
        Validator("VERSION", ne=1) | Validator("VERSION", ne=2),
        Validator("VERSION", ne=4) & Validator("VERSION", ne=2),
    )
    settings.validators.validate()


def test_negative_combined_or_validators(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)
    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )
    settings.validators.register(
        Validator("VERSION", ne=1) | Validator("VERSION", ne=1),
    )
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_negative_combined_and_validators(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)
    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )
    settings.validators.register(
        Validator("VERSION", ne=1) & Validator("VERSION", ne=1),
    )
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_envless_and_combined_validators(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    TOML = """
    value = true
    version = 1
    name = 'Bruno'
    """
    tmpfile.write(TOML)
    settings = LazySettings(
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile), silent=True
    )
    settings.validators.register(
        Validator("VERSION", ne=1) & Validator("value", ne=True),
    )
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_cast_before_validate(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    TOML = """
    name = 'Bruno'
    colors = ['red', 'green', 'blue']
    """
    tmpfile.write(TOML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        silent=True,
        lowercase_read=True,
        validators=[
            Validator("name", len_eq=5),
            Validator("name", len_min=1),
            Validator("name", len_max=5),
            Validator("colors", len_eq=3),
            Validator("colors", len_eq=3),
            Validator("colors", len_eq=24, cast=str),
        ],
    )
    assert settings.name == "Bruno"
    assert settings.colors == ["red", "green", "blue"]


def test_validator_can_provide_default(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    TOML = """
    name = 'Bruno'
    colors = ['red', 'green', 'blue']
    """
    tmpfile.write(TOML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=[
            Validator("name", required=True),
            Validator("FOO", default="BAR"),
            Validator("COMPUTED", default=lambda st, va: "I am computed"),
        ],
    )
    assert settings.name == "Bruno"
    assert settings.colors == ["red", "green", "blue"]

    assert settings.FOO == "BAR"
    assert settings.COMPUTED == "I am computed"
