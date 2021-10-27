import json
import os
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

import pytest

from dynaconf import Dynaconf
from dynaconf import SchemaExtraFields
from dynaconf import Field
from dynaconf import SchemaError
from dynaconf import SchemaValidationMode
from dynaconf import Validator


def test_schema_full(tmpdir, clean_env):
    os.environ["IS_FOO"] = "this_is_foo"
    os.environ["TLD"] = ".com"
    os.environ["TEST_SCHEMA_ONE_EMAIL"] = "not_be_loaded_default_is_forced"
    os.environ["TEST_SCHEMA_ONE_IGNORED"] = "this-is-not-loaded"
    os.environ["TEST_SCHEMA_ONE_DAY"] = "saturday"
    # os.environ["TEST_SCHEMA_ONE_CITY"] = "Rio"
    email_expr = "(this.name + '@' + this.company + env.TLD) | lower"

    settings_data = {
        "random_thing": True,
        "ignored_from_json": True,
    }
    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    @dataclass
    class MySchema(Dynaconf):
        city: str
        schema: int
        day: str
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
        b: str = "aaaa"
        a: int = Field(default_factory=lambda this: this.b.count("a"))

        class Config:
            extra_fields_policy = SchemaExtraFields.ignore

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

    # NOTE: FROM env vars this is not currently ignored (TBI)
    assert "ABCD" not in settings, settings.ABCD
    assert "IGNORED" not in settings, settings.IGNORED
    # but on files it is ignored
    assert "IGNORED_FROM_JSON" not in settings, settings.IGNORED_FROM_JSON


@pytest.mark.parametrize("schema_arg", ["schema", "dynaconf_schema"])
def test_schema_with_schema_arg(tmpdir, clean_env, schema_arg):
    """User can pass `schema` or `dynaconf_schema`"""

    @dataclass
    class MySchema(Dynaconf):
        name: str

    settings = Dynaconf(name="Bruno", **{schema_arg: MySchema})

    assert settings.name == "Bruno"


def test_schema_with_default_expr(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: int = Field(default_expr="40 + 2")

    settings = Dynaconf(
        schema=MySchema,
    )

    assert settings.number == 42


def test_schema_with_default_expr_raises_for_wrong_order(tmpdir, clean_env):

    # Wrong ordering
    @dataclass
    class MySchema(Dynaconf):
        number: int = Field(default_expr="this.truth + 2")
        truth: int = 40

    with pytest.raises(SchemaError):
        settings = Dynaconf(
            schema=MySchema,
        )

    # good ordering
    @dataclass
    class MySchema(Dynaconf):
        truth: int = 40
        number: int = Field(default_expr="this.truth + 2")

    settings = Dynaconf(
        schema=MySchema,
    )
    assert settings.number == 42


def test_schema_with_default_factory_raises_for_wrong_order(tmpdir, clean_env):

    # Wrong ordering
    @dataclass
    class MySchema(Dynaconf):
        number: int = Field(default_factory=lambda this: this.truth + 2)
        truth: int = 40

    with pytest.raises(SchemaError):
        Dynaconf(
            schema=MySchema,
        )

    # Good ordering
    @dataclass
    class MySchema(Dynaconf):
        truth: int = 40
        number: int = Field(default_factory=lambda this: this.truth + 2)

    settings = Dynaconf(
        schema=MySchema,
    )

    assert settings.number == 42


def test_schema_with_default_factory(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
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
    class MySchema(Dynaconf):
        number: int

    with pytest.raises(SchemaError):
        Dynaconf(schema=MySchema)  # number is missing


def test_schema_raise_for_missing_field(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: int = Field()

    with pytest.raises(SchemaError):
        Dynaconf(schema=MySchema)  # number is missing


def test_schema_raise_only_on_access_on_lazy_mode(tmpdir, clean_env):
    @dataclass
    class LazyMySchema(Dynaconf):
        number: int

        class Config:
            validation_mode = SchemaValidationMode.lazy

    @dataclass
    class EagerMySchema(Dynaconf):
        number: int

        class Config:
            validation_mode = SchemaValidationMode.eager

    with pytest.raises(SchemaError):
        Dynaconf(schema=EagerMySchema)  # number is missing

    settings = Dynaconf(schema=LazyMySchema)  # Do not validate schema
    with pytest.raises(SchemaError):
        # raise validation because of first access
        settings.number  # number is missing


def test_schema_raises_with_forbid_policy(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: int

        class Config:
            extra_fields_policy = SchemaExtraFields.forbid

    with pytest.raises(SchemaError) as excinfo:
        Dynaconf(
            schema=MySchema,
            number=10,
            other_thing_not_in_schema=10,
        )

    assert "other_thing_not_in_schema" in str(excinfo.value).lower()


def test_schema_do_not_raises_with_forbid_policy_from_env(tmpdir, clean_env):

    os.environ["TEST_FORBID_COISA"] = "NADA"

    @dataclass
    class MySchema(Dynaconf):
        number: int

        class Config:
            extra_fields_policy = SchemaExtraFields.forbid

    settings = Dynaconf(
        schema=MySchema, envvar_prefix="TEST_FORBID", number=10
    )

    # No error, but unknowm field is not set
    assert "COISA" not in settings


def test_schema_with_allow_policy(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: int

        class Config:
            extra_fields_policy = SchemaExtraFields.allow

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
    class MySchema(Dynaconf):
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
    assert settings.instance == MySchema
    assert settings.name == "Bruno"
    assert settings.name2 == "Bruno"
    assert settings.boolean1 is True
    assert settings.boolean2 is True
    assert settings.boolean3 is True


def test_schema_does_allow_typing_types(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Dynaconf):
        colors: List

    Dynaconf(schema=MySchema, colors=123)


def test_schema_allows_special_form_types(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Dynaconf):
        colors: Optional[list]

    Dynaconf(schema=MySchema, colors=["red"])


def test_schema_raises_for_invalid_casting(tmpdir, clean_env):
    """https://github.com/rochacbruno/dynaconf/issues/679"""

    @dataclass
    class MySchema(Dynaconf):
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
    class MySchema(Dynaconf):
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
    class MySchema(Dynaconf):
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
    class MySchema(Dynaconf):
        number: str = Field(validators=[Validator(gt=5, lt=10)])

    with pytest.raises(SchemaError):
        Dynaconf(
            dynaconf_schema=MySchema,
            number=2  # trigger validation error
            # number must gt 5 but it is 2 in env main
        )


def test_dynaconf_invalid_validator_raises(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: str = Field(validators=[1, True, {}])  # invalid validators

    with pytest.raises(SchemaError):
        Dynaconf(
            dynaconf_schema=MySchema,
        )


def test_compound_schema(tmpdir, clean_env):
    class CustomListOfThings:
        def __init__(self, value):
            self.value = value

    @dataclass
    class Options(Dynaconf):
        option1: str
        option2: str
        option3: int = Field(default=42)
        option4: int = Field(validators=[Validator(gt=50)])
        option5: Any = Field(default=None)
        option6: CustomListOfThings = Field(default=[1, 2, 3])
        option7: str = Field(validators=["value.startswith('banana')"])
        default_forced: str = Field(default="forced", force_default=True)

    @dataclass
    class Server(Dynaconf):
        host: str
        port: int
        options: Options
        another: int = Field(default=99)
        tags: CustomListOfThings = Field(default=["a", "b", "c"])
        default_forced: str = Field(default="forced", force_default=True)

    @dataclass
    class MySchema(Dynaconf):
        server: Server
        debug: bool = True
        colors: CustomListOfThings = Field(default=["red", "green", "blue"])

    os.environ["TEST_COMPOUND_SERVER__HOST"] = "localhost"
    os.environ["TEST_COMPOUND_SERVER__PORT"] = "1234"

    os.environ["TEST_COMPOUND_FOO"] = "bar"
    os.environ["TEST_COMPOUND_SERVER__FOO"] = "bar"
    os.environ["TEST_COMPOUND_SERVER__DEFAULT_FORCED"] = "bar"
    os.environ["TEST_COMPOUND_SERVER__options__OPTION1"] = "option1"
    os.environ["TEST_COMPOUND_SERVER__OPTIONS__opTion2"] = "option2"
    os.environ["TEST_COMPOUND_SERVER__optIons__optiOn4"] = "51"
    os.environ["TEST_COMPOUND_SERVER__options__Option7"] = "banana is good"
    os.environ["TEST_COMPOUND_SERVER__options__BLA"] = "Hello"
    os.environ["TEST_COMPOUND_SERVER__options__default_forced"] = "Hello"

    # os.environ["TEST_COMPOUND_SERVER__OPTIONS__option1"] = "option1"
    # os.environ["TEST_COMPOUND_SERVER__OPTIONS__option2"] = "option2"
    # os.environ["TEST_COMPOUND_SERVER__OPTIONS__option4"] = "51"
    # os.environ["TEST_COMPOUND_SERVER__OPTIONS__BLA"] = "Hello"

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
    assert settings.server.tags == ["a", "b", "c"]
    assert settings.server.options.option7 == "banana is good"
    assert settings.debug is True
    assert settings.colors == ["red", "green", "blue"]
    assert settings.server.default_forced == "forced"
    assert settings.server.options.default_forced == "forced"


def test_schema_as_a_dict(tmpdir, clean_env):

    Dynaconf(
        schema={
            "config": {
                "validation_mode": SchemaValidationMode.lazy,
                "extra_fields_policy": SchemaExtraFields.ignore,
            }
        }
    )

    # NOTE: Not implemented yet


def test_instantiate_schema():
    # this is not really used yet
    @dataclass
    class MySchema(Dynaconf):
        email: str = Field(default="bruno@foo.bar")

    schema = MySchema()
    assert schema.email.default == "bruno@foo.bar"


def test_multi_case_list_value(tmpdir, clean_env):
    settings_data = {
        "COLORS": ["white", "dynaconf_merge"],
    }
    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    os.environ["TEST_MULTI_COLORS"] = "@merge blue"
    os.environ["TEST_MULTI_SUB"] = "{colors=['gray', 'cyan']}"

    # NOTE: TBI: when there is a schema, env loader must load only matching
    # if extra_fields_policy is != allow
    # Also this must find closer match on casing if exact is not present.
    os.environ["TEST_MULTI_SUB__colors"] = "@merge green"

    # NOTE: should be ignored because is default for envvars
    os.environ["TEST_MULTI_COLORS_2"] = "red"
    os.environ["TEST_MULTI_COLORS_4"] = "red"
    os.environ["TEST_MULTI_COLORS_4"] = "red"
    os.environ["TEST_MULTI_HAUDFAJHBDJHBFSFHSDF"] = "red"

    @dataclass
    class Sub(Dynaconf):
        colors: list

    @dataclass
    class MySchema(Dynaconf):
        colors: list
        sub: Sub

        class Config:
            extra_fields_policy = SchemaExtraFields.forbid  # only count for files

    settings = Dynaconf(
        schema=MySchema,
        envvar_prefix="TEST_MULTI",
        settings_file=str(settings_file),
        colors=["red", "green"],
    )

    assert settings.colors == ["red", "green", "white", "blue"]
    assert settings.sub.colors == ["gray", "cyan", "green"]


def test_dir_method_includes_schema_data(tmpdir, clean_env):
    @dataclass
    class MySchema(Dynaconf):
        number: int = 1
        other: int = 2
        name: str = "foo"

    settings = Dynaconf(
        dynaconf_schema=MySchema,
    )

    dir_keys = dir(settings)
    assert "number" in dir_keys
    assert "other" in dir_keys
    assert "name" in dir_keys
