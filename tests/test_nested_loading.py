from __future__ import annotations

import pytest

from dynaconf.base import LazySettings


TOML = """
[default]
dynaconf_include = ["plugin1.toml", "plugin2.toml", "plugin2.toml"]
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
dynaconf_include = ["plugin1.toml", "plugin2.{0}"]
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

MIXED_MERGE = """
[default]
dynaconf_include = [
    "plugin1.toml",
    "plugin2.json",
    "plugin2.yaml",
    "plugin2.ini",
    "plugin2.py"
]
DEBUG = false
SERVER = "base.example.com"
PORT = 6666

[development]
DEBUG = false
SERVER = "dev.example.com"

[production]
DEBUG = false
SERVER = "prod.example.com"


[custom.nested_1]
base = 1

[custom.nested_1.nested_2]
base = 2

[custom.nested_1.nested_2.nested_3]
base = 3

[custom.nested_1.nested_2.nested_3.nested_4]
base = 4
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

[custom.nested_1.nested_2.nested_3.nested_4]
toml = 5
"""

TOML_PLUGIN_2 = """
[default]
SERVER = "plugin2.example.com"
PLUGIN_2_SPECIAL = true
PORT = 4040

[custom.nested_1.nested_2.nested_3.nested_4]
toml = 5
"""

TOML_PLUGIN_TEXT = """
[default]
database_uri = "toml.example.com"
port = 8080

[custom.nested_1.nested_2.nested_3.nested_4]
toml = 5
"""

JSON_PLUGIN_TEXT = """
{
    "default": {
        "database_uri": "json.example.com",
        "port": 8080
    },
    "custom": {
        "nested_1": {
            "nested_2": {
                "nested_3": {
                    "nested_4": {
                        "json": 5
                    }
                }
            }
        }
    }
}
"""

YAML_PLUGIN_TEXT = """
default:
  database_uri: "yaml.example.com"
  port: 8080

custom:
  nested_1:
    nested_2:
      nested_3:
        nested_4:
          yaml: 5
"""

INI_PLUGIN_TEXT = """
[default]
database_uri="ini.example.com"
port="@int 8080"

[custom]
  [[nested_1]]
    [[[nested_2]]]
      [[[[nested_3]]]]
          [[[[[nested_4]]]]]
            ini="@int 5"
"""

PY_PLUGIN_TEXT = """
DATABASE_URI = "py.example.com"
PORT = 8080
NESTED_1 = {
    "nested_2": {
        "nested_3": {
            "nested_4": {
                "py": 5
            }
        }
    }
}
"""

PLUGIN_TEXT = {
    "toml": TOML_PLUGIN_TEXT,
    "yaml": YAML_PLUGIN_TEXT,
    "json": JSON_PLUGIN_TEXT,
    "ini": INI_PLUGIN_TEXT,
    "py": PY_PLUGIN_TEXT,
}


def test_invalid_include_path(tmpdir):
    """Ensure non existing paths are not loaded."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(TOML)

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="DEFAULT",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
    )

    # Ensure overrides not happened
    assert settings.SERVER == "base.example.com"
    assert settings.DEBUG is False


def test_load_nested_toml(tmpdir):
    """Load a TOML file that includes other TOML files."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(TOML)

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(TOML_PLUGIN)

    toml_plugin_file = tmpdir.join("plugin2.toml")
    toml_plugin_file.write(TOML_PLUGIN_2)

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="DEFAULT",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        ROOT_PATH_FOR_DYNACONF=str(tmpdir),
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
    )

    # Ensure overrides that happen via TOML plugin config load.
    assert settings.SERVER == "plugin2.example.com"
    assert settings.DEBUG is False
    assert settings.PLUGIN_NAME == "testing"

    # From the second TOML plugin
    assert settings.PORT == 4040
    assert settings.PLUGIN_2_SPECIAL is True


@pytest.mark.parametrize("ext", ["toml", "json", "yaml", "ini", "py"])
def test_load_nested_different_types(ext, tmpdir):
    """Load a TOML file that includes other various settings file types."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(MIXED.format(ext))

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(TOML_PLUGIN)

    json_plugin_file = tmpdir.join(f"plugin2.{ext}")
    json_plugin_file.write(PLUGIN_TEXT[ext])

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="DEFAULT",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        ROOT_PATH_FOR_DYNACONF=str(tmpdir),
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URI == f"{ext}.example.com"
    assert settings.PORT == 8080
    assert settings.SERVER == "toml.example.com"
    assert settings.PLUGIN_NAME == "testing"


def test_load_nested_different_types_with_merge(tmpdir):
    """Check merge works for includes."""

    settings_file = tmpdir.join("settings.toml")
    settings_file.write(MIXED_MERGE)

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(TOML_PLUGIN)

    for ext in ["toml", "json", "yaml", "ini", "py"]:
        json_plugin_file = tmpdir.join(f"plugin2.{ext}")
        json_plugin_file.write(PLUGIN_TEXT[ext])

    settings = LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="custom",
        silent=False,
        LOADERS_FOR_DYNACONF=False,
        ROOT_PATH_FOR_DYNACONF=str(tmpdir),
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
        MERGE_ENABLED_FOR_DYNACONF=True,
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URI == f"{ext}.example.com"
    assert settings.PORT == 8080
    assert settings.SERVER == "toml.example.com"
    assert settings.PLUGIN_NAME == "testing"

    # merge asserts
    assert settings.NESTED_1.base == 1
    assert settings.NESTED_1.nested_2.base == 2
    assert settings.NESTED_1.nested_2.nested_3.base == 3
    assert settings.NESTED_1.nested_2.nested_3.nested_4.base == 4
    for ext in ["toml", "json", "yaml", "ini", "py"]:
        assert settings.NESTED_1.nested_2.nested_3.nested_4[ext] == 5


def test_programmatically_file_load(tmpdir):
    """Check file can be included programmatically"""
    settings_file = tmpdir.join("settings.toml")
    settings_file.write(
        """
       [default]
       default_var = 'default'
    """
    )

    settings = LazySettings(
        environments=True, SETTINGS_FILE_FOR_DYNACONF=str(settings_file)
    )
    assert settings.DEFAULT_VAR == "default"

    toml_plugin_file = tmpdir.join("plugin1.toml")
    toml_plugin_file.write(
        """
        [development]
        plugin_value = 'plugin'
    """
    )

    settings.load_file(path=str(toml_plugin_file))
    assert settings.PLUGIN_VALUE == "plugin"

    settings.setenv("production")
    assert settings.DEFAULT_VAR == "default"
    # programmatically loaded file is not persisted
    # once `env` is changed, or a `reload` it will be missed
    # to persist it needs to go to `INCLUDES_FOR_DYNACONF` variable
    with pytest.raises(AttributeError):
        assert settings.PLUGIN_VALUE == "plugin"


def test_include_via_python_module_name(tmpdir):
    """Check if an include can be a Python module name"""
    settings_file = tmpdir.join("settings.toml")
    settings_file.write(
        """
       [default]
       default_var = 'default'
    """
    )

    dummy_folder = tmpdir.mkdir("dummy")
    dummy_folder.join("dummy_module.py").write('FOO = "164110"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    settings = LazySettings(
        environments=True,
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
        INCLUDES_FOR_DYNACONF=["dummy.dummy_module"],
    )

    assert settings.DEFAULT_VAR == "default"
    assert settings.FOO == "164110"


def test_include_via_python_module_name_and_others(tmpdir):
    """Check if an include can be a Python module name plus others"""
    settings_file = tmpdir.join("settings.toml")
    settings_file.write(
        """
       [default]
       default_var = 'default'
    """
    )

    dummy_folder = tmpdir.mkdir("dummy")
    dummy_folder.join("dummy_module.py").write('FOO = "164110"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    yaml_file = tmpdir.join("otherfile.yaml")
    yaml_file.write(
        """
       default:
         yaml_value: 748632
    """
    )

    settings = LazySettings(
        environments=True,
        SETTINGS_FILE_FOR_DYNACONF=str(settings_file),
        INCLUDES_FOR_DYNACONF=["dummy.dummy_module", "otherfile.yaml"],
    )

    assert settings.DEFAULT_VAR == "default"
    assert settings.FOO == "164110"
    assert settings.YAML_VALUE == 748632
