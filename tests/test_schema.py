import json
import os
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

import pytest

from dynaconf import Dynaconf
from dynaconf import ExtraFields
from dynaconf import Field
from dynaconf import Schema
from dynaconf import SchemaEnvHolder
from dynaconf import SchemaError
from dynaconf import SchemaValidationMode
from dynaconf import Validator


def test_schema_full(tmpdir, clean_env):
    os.environ["IS_FOO"] = "this_is_foo"
    os.environ["TLD"] = ".com"
    os.environ["TEST_SCHEMA_ONE_EMAIL"] = "not_be_loaded_default_is_forced"
    os.environ["TEST_SCHEMA_ONE_IGNORED"] = "this-is-not-loaded"
    email_expr = "(this.name + '@' + this.company + env.TLD) | lower"

    settings_data = {
        "random_thing": True,
        "ignored_from_json": True,
    }
    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    @dataclass
    class MySchema(Schema):
        city: str
        schema: int
        a_thing: list = Field(default_factory=list)
        random_thing: bool = False  # will come from settings.json
        computed: int = Field(default_factory=lambda: 40 + 2)
        name_upper: str = Field(default_expr="this.name.upper()")
        name_reversed: str = Field(default_expr="this.name | reverse")
        company: str = "Acme"
        email: str = Field(default_expr=email_expr, force_default=True)
        name: str = Field(
            validators=["this.name != 'Bruno' and env.IS_FOO == 'this_is_foo'"]
        )
        age: int = Field(18, validators=[Validator(gt=1, lt=16)])
        banana: str = Field(validators=[lambda this: this.city == "Rio"])

        class Config:
            extra_fields_policy = ExtraFields.ignore

    settings = Dynaconf(
        settings_files=[str(settings_file)],
        envvar_prefix="TEST_SCHEMA_ONE",
        environments=False,
        load_dotenv=False,
        name="Bruno2",
        city="Rio",
        banana=1,
        age=15,
        schema=1,
        abcd=10,  # this will be ignored, because it's not in the schema
        dynaconf_schema=MySchema,
        random_thing=False,  # Json wins
    )

    assert settings.name == "Bruno2"
    assert "NAME" in settings
    assert "name" in settings
    assert settings.name_upper == "BRUNO2"
    assert settings.name_reversed == "2onurB"
    assert settings.company == "Acme"
    assert settings.email == "bruno2@acme.com"
    assert settings.age == 15
    assert settings.computed == 42
    assert settings.random_thing is True

    assert settings.load_dotenv_for_dynaconf is False

    assert "ABCD" not in settings, settings.ABCD
    assert "IGNORED" not in settings, settings.IGNORED
    assert "IGNORED_FROM_JSON" not in settings, settings.IGNORED_FROM_JSON


@pytest.mark.parametrize("schema_arg", ["schema", "dynaconf_schema"])
def test_schema_with_schema_arg(tmpdir, clean_env, schema_arg):
    """User can pass `schema` or `dynaconf_schema`"""

    @dataclass
    class MySchema(Schema):
        name: str

    settings = Dynaconf(name="Bruno", **{schema_arg: MySchema})

    assert settings.name == "Bruno"


def test_schema_with_default_expr(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int = Field(default_expr="40 + 2")

    settings = Dynaconf(
        schema=MySchema,
    )

    assert settings.number == 42


def test_schema_with_default_factory(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int = Field(default_factory=lambda: 40 + 2)

    settings = Dynaconf(
        schema=MySchema,
    )

    assert settings.number == 42


def test_field_with_default_and_expr_and_factory(tmpdir, clean_env):
    """only one of default, default_expr, default_factory can be set"""
    with pytest.raises(SchemaError):
        Field(default_expr="40 + 2", default=10)

    with pytest.raises(SchemaError):
        Field(default_factory=lambda: 1, default=10)

    with pytest.raises(SchemaError):
        Field(default_factory=lambda: 1, default_expr="40 + 2")

    # No error raised
    Field(default=1)
    Field(default_expr="40 + 2")
    Field(default_factory=lambda: 1)


def test_schema_raise_for_missing_attr(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int

    with pytest.raises(SchemaError):
        Dynaconf(schema=MySchema)  # number is missing


def test_schema_raise_for_missing_field(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int = Field()

    with pytest.raises(SchemaError):
        Dynaconf(schema=MySchema)  # number is missing


def test_schema_raise_only_on_access_on_lazy_mode(tmpdir, clean_env):
    @dataclass
    class LazyMySchema(Schema):
        number: int

        class Config:
            validation_mode = SchemaValidationMode.lazy

    @dataclass
    class EagerMySchema(Schema):
        number: int

        class Config:
            validation_mode = SchemaValidationMode.eager

    with pytest.raises(SchemaError):
        Dynaconf(schema=EagerMySchema)  # number is missing

    settings = Dynaconf(schema=LazyMySchema)  # Do not validate schema
    with pytest.raises(SchemaError):
        # raise validation because of first access
        settings.number  # number is missing


def test_schema_fails_if_key_not_upper_or_lower(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int

    with pytest.raises(SchemaError):
        MySchema._create(NumBer=10)


def test_schema_raises_with_forbid_policy(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int

        class Config:
            extra_fields_policy = ExtraFields.forbid

    with pytest.raises(SchemaError):
        Dynaconf(
            schema=MySchema,
            number=10,
            other_thing_not_in_schema=10,
        )


def test_schema_with_allow_policy(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: int

        class Config:
            extra_fields_policy = ExtraFields.allow

    settings = Dynaconf(
        schema=MySchema,
        number=10,
        other_thing_not_in_schema=10,
    )

    assert settings.number == 10
    assert settings.other_thing_not_in_schema == 10


def test_different_forms_of_default_factories(tmpdir, clean_env):
    """
    Test that the default factory can be passed as a callable or as a string
    """

    @dataclass
    class MySchema(Schema):
        number1: int = Field(default_factory=lambda: 40 + 2)
        number2: int = Field(default_factory=lambda this: this.number1 + 2)
        number3: int = Field(
            default_factory=lambda settings: settings.number1 + 2
        )
        number4: int = Field(default_factory=lambda st: st.number1 + 2)

        instance: Any = Field(default_factory=lambda schema: schema)

        name: str = Field(default="Bruno")
        name2: str = "Bruno"

        boolean1: bool = Field(default_expr="True")
        boolean2: bool = Field(default_expr="this.number1 == 42")
        boolean3: bool = Field(default_expr="settings.number1 == 42")

    settings = Dynaconf(
        schema=MySchema,
    )

    assert settings.number1 == 42
    assert settings.number2 == 44
    assert settings.number3 == 44
    assert settings.number4 == 44
    assert settings.instance.__class__ == MySchema
    assert settings.name == "Bruno"
    assert settings.name2 == "Bruno"
    assert settings.boolean1 is True
    assert settings.boolean2 is True
    assert settings.boolean3 is True


def test_schema_does_allow_typing_types(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Schema):
        colors: List

    Dynaconf(schema=MySchema, colors=123)


def test_schema_allows_special_form_types(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Schema):
        colors: Optional[list]

    Dynaconf(schema=MySchema, colors=["red"])


def test_schema_raises_for_invalid_casting(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Schema):
        number: int

    with pytest.raises(SchemaError):
        Dynaconf(schema=MySchema, number=[1, 2, 3])


def test_default_values_ignored_when_found(tmpdir, clean_env):
    os.environ["TEST_DEFAULT_EMAIL"] = "not_be_loaded_default_is_forced"
    settings_data = {
        "ignored_settings": "this is not loaded",
    }

    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    @dataclass
    class MySchema(Schema):
        email: str = Field(default="default@email.com")
        ignored_settings: str = Field(default="default_value")
        ignored_attr: int = Field(default=42)

    settings = Dynaconf(
        settings_files=[str(settings_file)],
        envvar_prefix="TEST_DEFAULT",
        dynaconf_schema=MySchema,
        ignored_attr=10,
    )

    assert settings.email == "not_be_loaded_default_is_forced"
    assert settings.ignored_settings == "this is not loaded"
    assert settings.ignored_attr == 10


def test_default_values_forced(tmpdir, clean_env):
    os.environ["TEST_FORCE_EMAIL"] = "not_be_loaded_default_is_forced"
    settings_data = {
        "ignored_settings": "this is not loaded",
    }

    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    @dataclass
    class MySchema(Schema):
        email: str = Field(default="default@email.com", force_default=True)
        ignored_settings: str = Field(default="default_va", force_default=True)
        ignored_attr: int = Field(default=42, force_default=True)

    settings = Dynaconf(
        settings_files=[str(settings_file)],
        envvar_prefix="TEST_FORCE",
        dynaconf_schema=MySchema,
        ignored_attr=10,
    )

    assert settings.email == "default@email.com"
    assert settings.ignored_settings == "default_va"
    assert settings.ignored_attr == 42


def test_dynaconf_legacy_validators_raises(tmpdir, clean_env):
    @dataclass
    class MySchema(Schema):
        number: str = Field(validators=[Validator(gt=5, lt=10)])

    with pytest.raises(SchemaError):
        Dynaconf(
            dynaconf_schema=MySchema,
            number=2  # trigger validation error
            # number must gt 5 but it is 2 in env main
        )


def test_multi_env_schema(tmpdir, clean_env):
    settings_data = {
        "development": {
            "user": "dev_user",
            "port": 1234,  # on dev port is int
        },
        "production": {
            "user": "prod_user",
            "port": [5675, 5676],  # on prod port is list
        },
    }
    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    @dataclass
    class DevSchema(Schema):
        user: str
        port: int

        class Config:
            extra_fields_policy = ExtraFields.ignore

    @dataclass
    class ProdSchema(Schema):
        user: int  # wrong on purpose to trigger error
        port: List[int]

    settings = Dynaconf(
        settings_files=[str(settings_file)],
        environments=True,
        extra_field=134,
        schema=SchemaEnvHolder(
            development=DevSchema,
            production=ProdSchema,
        ),
    )

    assert settings.user == "dev_user"
    assert "extra_field" not in settings

    os.environ["MULTI_ENV_ENV"] = "production"
    with pytest.raises(SchemaError):
        settings = Dynaconf(
            settings_files=[str(settings_file)],
            env_switcher="MULTI_ENV_ENV",
            environments=True,
            schema=SchemaEnvHolder(
                development=DevSchema,
                production=ProdSchema,
            ),
        )


def test_compound_schema(tmpdir, clean_env):
    class CustomListOfThings:
        def __init__(self, value):
            self.value = value

    @dataclass
    class Options(Schema):
        option1: str
        option2: str
        option3: int = Field(default=42)
        option4: int = Field(validators=[Validator(gt=50)])
        option5: Any = Field(default=None)
        option6: CustomListOfThings = Field(default=[1, 2, 3])

    @dataclass
    class Server(Schema):
        host: str
        port: int
        options: Options
        another: int = Field(default=99)
        tags: CustomListOfThings = Field(default=["a", "b", "c"])

    @dataclass
    class MySchema(Schema):
        server: Server
        debug: bool = True
        colors: CustomListOfThings = Field(default=["red", "green", "blue"])

    os.environ["TEST_COMPOUND_SERVER__HOST"] = "localhost"
    os.environ["TEST_COMPOUND_SERVER__PORT"] = "1234"

    # NOTE: make it work with mixed keys
    # os.environ["TEST_COMPOUND_SERVER__options__OPTION1"] = "option1"
    # os.environ["TEST_COMPOUND_SERVER__OPTIONS__option2"] = "option2"
    # os.environ["TEST_COMPOUND_SERVER__options__option4"] = "51"
    # os.environ["TEST_COMPOUND_SERVER__options__BLA"] = "Hello"

    os.environ["TEST_COMPOUND_SERVER__OPTIONS__option1"] = "option1"
    os.environ["TEST_COMPOUND_SERVER__OPTIONS__option2"] = "option2"
    os.environ["TEST_COMPOUND_SERVER__OPTIONS__option4"] = "51"
    os.environ["TEST_COMPOUND_SERVER__OPTIONS__BLA"] = "Hello"

    settings = Dynaconf(
        schema=MySchema,
        envvar_prefix="TEST_COMPOUND",
    )

    assert settings.server.host == "localhost"
    assert settings.server.port == 1234
    assert settings.server.options.option1 == "option1"
    assert settings.server.options.option2 == "option2"
    assert settings.server.options.option3 == 42
    assert settings.server.options.option4 == 51
    assert settings.server.options.option5 is None
    assert settings.server.another == 99
