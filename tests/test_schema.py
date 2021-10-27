import json
import os
from typing import List

from dynaconf import Dynaconf
from dynaconf import Validator
from dynaconf.schema import Field
from dynaconf.schema import SchemaExtraFields
from dynaconf.schema import SchemaValidationMode


def test_schema_less(tmpdir, clean_env):
    settings_data = {
        "server": "localhost",
        "port": 4242,
        "databases": {"default": {"engine": "mysql"}},
    }
    settings_file = tmpdir.join("settings.json")
    settings_file.write(json.dumps(settings_data))

    os.environ["MYPROGRAM_NAME"] = "Bruno"
    os.environ["MYPROGRAM_DATABASES__default__engine"] = "sqlite"

    settings = Dynaconf(
        foo="bar", settings_file=str(settings_file), envvar_prefix="MYPROGRAM"
    )

    assert settings.FOO == "bar"
    assert settings.NAME == "Bruno"
    assert settings.PORT == 4242
    assert settings.port == 4242
    assert settings.get("port") == 4242
    assert settings("port") == 4242
    assert settings["port"] == 4242
    assert settings._store["port"] == 4242
    assert settings.SERVER == "localhost"
    assert settings.server == "localhost"
    assert settings.DATABASES.default.ENGINE == "sqlite"


def test_schema_full(tmpdir, clean_env):

    settings_data = {
        "random_thing": True,
        "ignored_from_json": True,
        "config": "my_config",
        "colors": 123,  # must break
    }
    json_file = tmpdir.join("settings.json")
    json_file.write(json.dumps(settings_data))

    os.environ["MYPROGRAM2_NAME"] = "Bruno"
    os.environ["MYPROGRAM2_SERVER"] = "localhost"
    os.environ["MYPROGRAM2_COLORS"] = "['red']"
    os.environ["MYPROGRAM2_BANANA"] = "The Banana"
    os.environ["MYPROGRAM2_BAR"] = "The Bar"

    class Settings(Dynaconf):
        bar = "zaz"
        banana: str
        colors: List[str]
        meh: int = 0
        server: str
        hdf = "33"
        name: str = Field(validators=["value == 'Bruno'"])

        class SchemaConfig:
            extra_fields_policy = SchemaExtraFields.allow
            validation_mode = SchemaValidationMode.eager
            envvar_prefix = "MYPROGRAM2"

    settings = Settings(
        foo="bar", settings_file=str(json_file), envvar_prefix="MYPROGRAM2"
    )

    assert settings.__schema_config__().envvar_prefix == "MYPROGRAM2"
    assert settings.config == "my_config"

    assert settings.FOO == "bar"
    assert settings.BAR == "The Bar"
    assert settings.bar == "The Bar"
    assert settings.RANDOM_THING is True
    assert settings.SERVER == "localhost"
    assert settings.server == "localhost"
    assert settings.NAME == "Bruno"


def test_schema_with_fields_and_defaults(tmpdir, clean_env):
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

    class Settings(Dynaconf):
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

        class SchemaConfig:
            extra_fields_policy = SchemaExtraFields.ignore

    settings = Settings(
        settings_files=[str(settings_file)],
        envvar_prefix="TEST_SCHEMA_ONE",
        environments=False,
        load_dotenv=False,
        name="Bruno2",
        city="Rio",
        banana="fruta",
        age=15,
        schema=1,
        abcd=10,  # this will be ignored, because it's not in the schema
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
