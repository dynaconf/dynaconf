import os
from dynaconf.base import LazySettings


TOML = """
[default]
dynaconf_include = ["plugin1.toml", "plugin2.toml"]
DEBUG = false
SERVER = "base.example.com"
PORT = 6666

[development]
DEBUG = false
SERVER = "dev.example.com"

[production]
DEBUG = false
SERVER = "prod.example.com"
"""

MIXED = """
[default]
dynaconf_include = ["plugin1.toml", "plugin2.json"]
DEBUG = false
SERVER = "base.example.com"
PORT = 6666

[development]
DEBUG = false
SERVER = "dev.example.com"

[production]
DEBUG = false
SERVER = "prod.example.com"
"""

TOML_PLUGIN = """
[default]
SERVER = "toml.example.com"
PLUGIN_NAME = "testing"

[development]
SERVER = "toml.example.com"
PLUGIN = "extra development var"

[production]
SERVER = "toml.example.com"
PLUGIN = "extra production var"
"""

TOML_PLUGIN_2 = """
[default]
SERVER = "plugin2.example.com"
PLUGIN_2_SPECIAL = true
PORT = 4040
"""

JSON_PLUGIN = """
{"default": {"database_uri": "json.example.com", "port": 8080}}
"""


def test_load_nested_toml(tmpdir):
    """Load a TOML file that includes other TOML files."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(TOML)

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(TOML_PLUGIN)

    toml_plugin_file = tmpdir.join("plugin2.toml")
    toml_plugin_file.write(TOML_PLUGIN_2)

    settings = LazySettings(
        ENV_FOR_DYNACONF="DEFAULT",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        SETTINGS_MODULE_FOR_DYNACONF=str(settings_file))

    # Ensure overrides that happen via TOML plugin config load.
    assert settings.SERVER == "plugin2.example.com"
    assert settings.DEBUG is False
    assert settings.PLUGIN_NAME == "testing"

    # From the second TOML plugin
    assert settings.PORT == 4040
    assert settings.PLUGIN_2_SPECIAL is True


def test_load_nested_different_types(tmpdir):
    """Load a TOML file that includes other various settings file types."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(MIXED)

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(TOML_PLUGIN)

    json_plugin_file = tmpdir.join("plugin2.json")
    json_plugin_file.write(JSON_PLUGIN)

    settings = LazySettings(
        ENV_FOR_DYNACONF="DEFAULT",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        SETTINGS_MODULE_FOR_DYNACONF=str(settings_file))

    assert settings.DEBUG is False
    assert settings.DATABASE_URI == "json.example.com"
    assert settings.PORT == 8080
    assert settings.SERVER == "toml.example.com"
    assert settings.PLUGIN_NAME == "testing"
