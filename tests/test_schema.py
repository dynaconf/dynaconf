import json
import os
from typing import List

from dynaconf import Dynaconf
from dynaconf.schema import ExtraFields
from dynaconf.schema import Field
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

    os.environ["MYPROGRAM_NAME"] = "Bruno"
    os.environ["MYPROGRAM_SERVER"] = "localhost"
    os.environ["MYPROGRAM_COLORS"] = "localhost"

    class Settings(Dynaconf):
        bar = "zaz"
        banana: str  # must break, no default value, no value provided
        colors: List[str]
        meh: int = None
        server: str = "myserver"
        hdf = "33"

        class SchemaConfig:
            extra_fields_policy = ExtraFields.allow
            validation_mode = SchemaValidationMode.eager
            envvar_prefix = "MYPROGRAM"

    settings = Settings(
        foo="bar", settings_file=str(json_file), envvar_prefix="MYPROGRAM"
    )

    assert settings.__schema_config__().envvar_prefix == "MYPROGRAM"
    assert settings.config == "my_config"

    # __import__("ipdb").set_trace()

    assert settings.FOO == "bar"
    assert settings.RANDOM_THING is True
    # assert settings.server == 'localhost'
    assert settings.SERVER == "localhost"
    # assert settings.NAME == 'Bruno'
