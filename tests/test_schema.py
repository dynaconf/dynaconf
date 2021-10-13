import json
import os
from dataclasses import dataclass
from typing import List

from dynaconf import Dynaconf
from dynaconf import ExtraFields
from dynaconf import Field
from dynaconf import Schema
from dynaconf import Validator


def test_schema(tmpdir, clean_env):
    os.environ["IS_FOO"] = "this_is_foo"
    os.environ["TLD"] = ".com"
    os.environ["DYNACONF_EMAIL"] = "this_will_not_be_loaded_default_is_forced"
    os.environ["DYNACONF_IGNORED"] = "this-is-not-loaded"
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
        a_thing: List = Field(default_factory=list)
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
        envvar_prefix="DYNACONF_",
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
