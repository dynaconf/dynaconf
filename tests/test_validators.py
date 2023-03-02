from __future__ import annotations

import os
from types import MappingProxyType

import pytest

from dynaconf import Dynaconf
from dynaconf import LazySettings
from dynaconf import ValidationError
from dynaconf import Validator
from dynaconf.validator import ValidatorList


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

YAML = """
server:
    hostname: "localhost"
    port: 22
    users:
      - "Bruno"
      - "Lula"
app:
    name: "testname"
    path: "/tmp/app_startup"
    args:
        arg1: "a"
        arg2: "b"
        arg3: "c"

hasemptyvalues:
    key1:
    key2:
    key3: null
    key4: "@empty"
"""


@pytest.fixture
def yaml_validators_good():
    return [
        Validator(
            "server.hostname", "server.port", "server.users", must_exist=True
        ),
        Validator(
            "app.name",
            "app.path",
            "app.args.arg1",
            "app.args.arg2",
            "app.args.arg3",
            must_exist=True,
        ),
    ]


@pytest.fixture
def yaml_validators_bad():
    return [
        Validator("missing.value", must_exist=True),
        Validator("app.missing", must_exist=True),
        Validator("app.args.missing", must_exist=True),
    ]


@pytest.fixture
def yaml_validators_mixed(yaml_validators_good, yaml_validators_bad):
    mixed = []
    mixed.extend(yaml_validators_good)
    mixed.extend(yaml_validators_bad)
    return mixed


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


def test_validate_all(tmpdir):
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
        Validator("BLABLABLA", must_exist=True),
    )

    with pytest.raises(ValidationError) as error:
        settings.validators.validate_all()

    assert (
        custom_msg.format(name="VERSION", value="1", env="DEVELOPMENT")
        in error.value.message
    )
    assert "BLABLABLA" in error.value.message

    assert error.type == ValidationError
    assert len(error.value.details) == 2


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


def test_cast_on_validate_transforms_value(tmpdir):
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
            # Order matters here
            Validator("name", len_eq=5),
            Validator("name", len_min=1),
            Validator("name", len_max=5),
            # This will cast the str to list
            Validator("name", cast=list),
            Validator("colors", len_eq=3),
            Validator("colors", len_eq=3),
            # this will cast the list to str
            Validator("colors", len_eq=24, cast=str),
        ],
    )
    assert settings.name == list("Bruno")
    assert settings.colors == str(["red", "green", "blue"])


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


def test_validator_init_exclude(tmpdir, yaml_validators_mixed):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=yaml_validators_mixed,
        validate_exclude=["missing", "app.missing", "app.args.missing"],
    )
    assert settings.server.hostname == "localhost"


def test_validator_init_only(tmpdir, yaml_validators_mixed):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=yaml_validators_mixed,
        validate_only=["server"],
    )
    assert settings.server.hostname == "localhost"


def test_validator_init_mixed(tmpdir, yaml_validators_mixed):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=yaml_validators_mixed,
        validate_only=["server", "app"],
        validate_exclude=["app.missing", "app.args.missing"],
    )
    assert settings.server.hostname == "localhost"


def test_validator_only_post_register(
    tmpdir, yaml_validators_good, yaml_validators_bad
):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=yaml_validators_good,
        validate_only=["server"],
    )
    assert settings.server.hostname == "localhost"
    settings.validators.register(*yaml_validators_bad)
    # call validation only on the server section
    settings.validators.validate(only=["server"])


def test_validator_exclude_post_register(
    tmpdir, yaml_validators_good, yaml_validators_bad
):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        validators=yaml_validators_good,
        validate_only=["server", "app.path"],
    )
    assert settings.server.hostname == "localhost"
    settings.validators.register(*yaml_validators_bad)
    # call validation only on the server section
    settings.validators.validate(
        exclude=["missing", "app.missing", "app.args.missing"]
    )
    settings.app.path = "/tmp/app_startup"


def test_validator_only_current_env_valid(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        environments=True,
        ENV_FOR_DYNACONF="DEVELOPMENT",
    )
    settings.validators.register(
        Validator("IMAGE_1", env="production", must_exist=True)
    )
    settings.validators.validate(only_current_env=True)


def test_raises_only_current_env_invalid(tmpdir):
    tmpfile = tmpdir.join("settings.toml")
    tmpfile.write(TOML)
    settings = LazySettings(
        settings_file=str(tmpfile),
        environments=True,
        ENV_FOR_DYNACONF="PRODUCTION",
    )
    settings.validators.register(
        Validator("IMAGE_1", env="production", must_exist=True)
    )

    with pytest.raises(ValidationError):
        settings.validators.validate(only_current_env=True)


def test_raises_on_invalid_selective_args(tmpdir, yaml_validators_good):
    settings = LazySettings(validators=yaml_validators_good, validate_only=int)
    with pytest.raises(ValueError):
        settings.validator_instance.validate()

    settings = LazySettings(
        validators=yaml_validators_good, validate_exclude=int
    )
    with pytest.raises(ValueError):
        settings.validator_instance.validate()


def test_validator_descriptions(tmpdir):
    validators = ValidatorList(
        LazySettings(),
        validators=[
            Validator("foo", description="foo"),
            Validator("bar", description="bar"),
            Validator("baz", "zaz", description="baz zaz"),
            Validator("foo", description="another message"),
            Validator("a", description="a") & Validator("b"),
        ],
    )

    assert validators.descriptions() == {
        "bar": ["bar"],
        "baz": ["baz zaz"],
        "zaz": ["baz zaz"],
        "foo": ["foo", "another message"],
        "a": ["a"],
        "b": ["a"],
    }


def test_validator_descriptions_flat(tmpdir):
    validators = ValidatorList(
        LazySettings(),
        validators=[
            Validator("foo", description="foo"),
            Validator("bar", description="bar"),
            Validator("baz", "zaz", description="baz zaz"),
            Validator("foo", description="another message"),
            Validator("a", description="a") & Validator("b"),
        ],
    )

    assert validators.descriptions(flat=True) == {
        "bar": "bar",
        "baz": "baz zaz",
        "zaz": "baz zaz",
        "foo": "foo",
        "a": "a",
        "b": "a",
    }


def test_toml_should_not_change_validator_type_with_is_type_set():
    settings = Dynaconf(
        validators=[Validator("TEST", is_type_of=str, default="+172800")]
    )

    assert settings.test == "+172800"


def test_toml_should_not_change_validator_type_with_is_type_not_set_int():
    settings = Dynaconf(
        validators=[Validator("TEST", default="+172800")]
        # The ways to force a string is
        # passing is_type_of=str
        # or default="@str +172800" or default="'+172800'"
    )

    assert settings.test == +172800


def test_toml_should_not_change_validator_type_using_at_sign():
    settings = Dynaconf(
        validators=[Validator("TEST", is_type_of=str, default="@str +172800")]
    )

    assert settings.test == "+172800"


def test_default_eq_env_lvl_1():
    """Tests when the env value equals the default value."""
    VAR_NAME = "test"
    ENV = "DYNATESTRUN_TEST"
    settings = Dynaconf(
        environments=False,
        envvar_prefix="DYNATESTRUN",
        validators=[
            Validator(
                VAR_NAME,
                default=True,
                is_type_of=bool,
            ),
        ],
    )
    os.environ[ENV] = "true"
    assert settings.test is True
    del os.environ[ENV]


def test_default_lvl_1():
    """Tests if the default works properly without any nested level.

    Uses different values for the default and the environment variable.
    """
    VAR_NAME = "test"
    ENV = "DYNATESTRUN_TEST"
    settings = Dynaconf(
        environments=False,
        envvar_prefix="DYNATESTRUN",
        validators=[
            Validator(
                VAR_NAME,
                default=True,
                is_type_of=bool,
            ),
        ],
    )
    os.environ[ENV] = "false"
    assert settings.test is False
    del os.environ[ENV]


def test_default_lvl_2():
    """Tests if the default works properly with one nested level.

    Uses different values for the default and the environment variable.
    """
    VAR_NAME = "nested.test"
    ENV = "DYNATESTRUN_NESTED__TEST"
    settings = Dynaconf(
        environments=False,
        envvar_prefix="DYNATESTRUN",
        validators=[
            Validator(
                VAR_NAME,
                default=True,
                is_type_of=bool,
            ),
        ],
    )
    os.environ[ENV] = "false"
    assert settings.nested.test is False
    del os.environ[ENV]


def test_use_default_value_when_yaml_is_empty_and_explicitly_marked(tmpdir):
    tmpfile = tmpdir.join("settings.yaml")
    tmpfile.write(YAML)
    settings = Dynaconf(
        settings_file=str(tmpfile),
        validators=[
            # Explicitly say thar default must be applied to None
            Validator(
                "hasemptyvalues.key1",
                default="value1",
                apply_default_on_none=True,
            ),
            # The following 2 defaults must be ignored
            Validator("hasemptyvalues.key2", default="value2"),
            Validator("hasemptyvalues.key3", default="value3"),
            # This one must be set because on YAML key is set to `@empty`
            Validator("hasemptyvalues.key4", default="value4"),
        ],
    )
    assert settings.hasemptyvalues.key1 == "value1"
    assert settings.hasemptyvalues.key2 is None
    assert settings.hasemptyvalues.key3 is None
    assert settings.hasemptyvalues.key4 == "value4"


def test_ensure_cast_happens_after_must_exist(tmpdir):
    """#823"""
    from pathlib import Path

    settings = Dynaconf(
        validators=[Validator("java_bin", must_exist=True, cast=Path)]
    )
    # must raise ValidationError instead of Path error
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_ensure_cast_works_for_non_default_values(tmpdir):
    """#834"""

    settings = Dynaconf(validators=[Validator("offset", default=1, cast=int)])

    settings.offset = "24"

    settings.validators.validate()

    assert isinstance(settings.offset, int), type(settings.offset)
