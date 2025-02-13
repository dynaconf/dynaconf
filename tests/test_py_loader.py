from __future__ import annotations

import os

import pytest

from dynaconf import default_settings
from dynaconf import LazySettings
from dynaconf.loaders.py_loader import load
from dynaconf.loaders.py_loader import try_to_load_from_py_module_name
from dynaconf.utils import DynaconfDict


def test_py_loader_from_file(tmpdir):
    settings = DynaconfDict()
    dummy_path = tmpdir.join("dummy_module.py")
    with open(
        str(dummy_path), "w", encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write('FOO = "bar"')

    load(settings, "dummy_module.py")
    os.remove("dummy_module.py")
    load(settings, "dummy_module.py")  # will be ignored not found

    assert settings.get("FOO") == "bar"


def test_py_loader_from_module(tmpdir):
    settings = DynaconfDict()
    dummy_folder = tmpdir.mkdir("dummy")

    dummy_folder.join("dummy_module.py").write('FOO = "bar"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    load(settings, "dummy.dummy_module")

    assert settings.exists("FOO")


def test_try_to_load_from_py_module_name(tmpdir):
    settings = DynaconfDict()
    dummy_folder = tmpdir.mkdir("dummy")

    dummy_folder.join("dummy_module.py").write('FOO = "bar"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    try_to_load_from_py_module_name(settings, "dummy.dummy_module")

    assert settings.exists("FOO")


def test_negative_try_to_load_from_py_module_name(tmpdir):
    settings = DynaconfDict()
    with pytest.raises(ImportError):
        try_to_load_from_py_module_name(settings, "foo.bar.dummy")


def test_silently_try_to_load_from_py_module_name(tmpdir):
    settings = DynaconfDict()
    try_to_load_from_py_module_name(settings, "foo.bar.dummy", silent=True)

    assert settings.exists("FOO") is False


def test_py_loader_from_file_dunder(clean_env, tmpdir):
    """Test load with dunder settings"""

    settings = LazySettings(
        DATABASES={
            "default": {
                "NAME": "db",
                "ENGINE": "module.foo.engine",
                "ARGS": {"timeout": 30},
                "PORTS": [123, 456],
            }
        }
    )
    dummy_path = tmpdir.join("dummy_module.py")
    with open(
        str(dummy_path), "w", encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write('F = "bar"')
        f.write("\n")
        f.write('COLORS__white__code = "#FFFFFF"')
        f.write("\n")
        f.write('DATABASES__default__ENGINE = "other.module"')

    load(settings, "dummy_module.py")
    os.remove("dummy_module.py")
    load(settings, "dummy_module.py")  # will be ignored not found

    assert settings.get("F") == "bar"
    assert settings.COLORS == {"white": {"code": "#FFFFFF"}}
    assert settings.DATABASES.default.NAME == "db"
    assert settings.DATABASES.default.ENGINE == "other.module"


def test_decorated_hooks(clean_env, tmpdir):
    # Arrange
    settings_path = tmpdir.join("settings.py")
    settings_extra = tmpdir.join("extra.py")

    to_write = {
        str(settings_path): [
            "INSTALLED_APPS = ['admin']",
            "COLORS = ['red', 'green']",
            "DATABASES = {'default': {'NAME': 'db'}}",
            "BANDS = ['Rush', 'Yes']",
            "from dynaconf import post_hook",
            "@post_hook",
            "def post_hook(settings):",
            "    return {",
            "        'INSTALLED_APPS': ['admin', 'plugin'],",
            "        'COLORS': '@merge blue',",
            "        'DATABASES__default': '@merge PORT=5151',",
            "        'DATABASES__default__VERSION': 42,",
            "        'DATABASES__default__FORCED_INT': '@int 12',",
            "        'BANDS': ['Anathema', 'dynaconf_merge'],",
            "    }",
        ],
        str(settings_extra): [
            "NAME = 'Bruce'",
            "BASE_PATH = '/etc/frutaria'",
            "from dynaconf import post_hook",
            "@post_hook",
            "def post_hook(settings):",
            "    return {",
            "        'INSTALLED_APPS': ['admin', 'extra'],",
            "        'COLORS': '@merge yellow',",
            "        'DATABASES__default': '@merge PORT=5152',",
            "        'DATABASES__default__VERSION': 43,",
            "        'DATABASES__default__FORCED_INT': '@int 13',",
            "        'BANDS': ['Opeth', 'dynaconf_merge'],",
            # Not sure @format should be supported on hooks, as settings is available on scope.
            # maybe useful to set as a lazy value to be resolved after all hooks are executed.
            "        'FULL_NAME': '@format {this.NAME} Rock',",
            "        'FULL_PATH': f'{settings.BASE_PATH}/batata/',",
            "    }",
        ],
    }

    for path, lines in to_write.items():
        with open(
            str(path), "w", encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as f:
            for line in lines:
                f.write(line)
                f.write("\n")

    # Act
    settings = LazySettings(settings_file="settings.py")

    # Assert
    # settings has _post_hooks attribute with one hook registered
    assert settings._post_hooks
    assert len(settings._post_hooks) == 1

    # assert values set by the first hook only
    assert settings.INSTALLED_APPS == ["admin", "plugin"]
    assert settings.COLORS == ["red", "green", "blue"]
    assert settings.DATABASES.default.NAME == "db"
    assert settings.DATABASES.default.PORT == 5151
    assert settings.DATABASES.default.VERSION == 42
    assert settings.DATABASES.default.FORCED_INT == 12
    assert settings.BANDS == ["Rush", "Yes", "Anathema"]

    # Call load_file to load the second file
    settings.load_file(str(settings_extra))

    # assert _post_hooks attribute has two hooks registered
    assert len(settings._post_hooks) == 2

    # assert values set by the second hook only
    assert settings.INSTALLED_APPS == ["admin", "extra"]
    assert settings.COLORS == ["red", "green", "blue", "yellow"]
    assert settings.DATABASES.default.NAME == "db"
    assert settings.DATABASES.default.PORT == 5152
    assert settings.DATABASES.default.VERSION == 43
    assert settings.DATABASES.default.FORCED_INT == 13
    assert settings.BANDS == ["Rush", "Yes", "Anathema", "Opeth"]
    assert settings.FULL_NAME == "Bruce Rock"
    assert settings.FULL_PATH == "/etc/frutaria/batata/"


def test_post_load_hooks(clean_env, tmpdir):
    """Test post load hooks works

    This test uses 3 settings files

    PRELOAD = "plugin_folder/plugin.py"
    SETTINGS_FILE = "settings.py"
    HOOKFILES = ["plugin_folder/dynaconf_hooks.py", "dynaconf_hooks.py"]

    The hook file has a function called "post" which is called after
    loading the settings, that function accepts the argument `settings`
    which is a copy of the settings object, and returns a dictionary
    of settings to be merged.
    """

    # Arrange
    plugin_folder = tmpdir.mkdir("plugin_folder")
    plugin_folder.join("__init__.py").write('print("initing plugin...")')

    plugin_path = plugin_folder.join("plugin.py")
    plugin_hook = plugin_folder.join("dynaconf_hooks.py")
    settings_path = tmpdir.join("settings.py")
    settings_hook = tmpdir.join("dynaconf_hooks.py")

    to_write = {
        str(plugin_path): ["PLUGIN_NAME = 'DummyPlugin'"],
        str(settings_path): [
            "INSTALLED_APPS = ['admin']",
            "COLORS = ['red', 'green']",
            "DATABASES = {'default': {'NAME': 'db'}}",
            "BANDS = ['Rush', 'Yes']",
        ],
        str(plugin_hook): [
            "post = lambda settings: "
            "{"
            "'PLUGIN_NAME': settings.PLUGIN_NAME.lower(),"
            "'COLORS': '@merge blue',"
            "'DATABASES__default': '@merge PORT=5151',"
            "'DATABASES__default__VERSION': 42,"
            "'DATABASES__default__FORCED_INT': '@int 12',",
            "'BANDS': ['Anathema', 'dynaconf_merge']" "}",
        ],
        str(settings_hook): [
            "post = lambda settings: "
            "{"
            "'INSTALLED_APPS': [settings.PLUGIN_NAME],"
            "'dynaconf_merge': True,"
            "}"
        ],
    }

    for path, lines in to_write.items():
        with open(
            str(path), "w", encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as f:
            for line in lines:
                f.write(line)
                f.write("\n")

    # Act
    settings = LazySettings(
        preload=["plugin_folder.plugin"], settings_file="settings.py"
    )

    # Assert
    assert settings.PLUGIN_NAME == "dummyplugin"
    assert settings.INSTALLED_APPS == ["admin", "dummyplugin"]
    assert settings.COLORS == ["red", "green", "blue"]
    assert settings.DATABASES.default.NAME == "db"
    assert settings.DATABASES.default.PORT == 5151
    assert settings.DATABASES.default.VERSION == 42
    assert settings.DATABASES.default.FORCED_INT == 12
    assert settings.BANDS == ["Rush", "Yes", "Anathema"]

    plugin_hook, settings_hook = list(settings._loaded_hooks.keys())
    assert settings._loaded_hooks[plugin_hook] == {
        "post": {
            "PLUGIN_NAME": "dummyplugin",
            "COLORS": "@merge blue",
            "DATABASES__default": "@merge PORT=5151",
            "DATABASES__default__VERSION": 42,
            "DATABASES__default__FORCED_INT": "@int 12",
            "BANDS": ["Anathema", "dynaconf_merge"],
        }
    }
    assert settings._loaded_hooks[settings_hook] == {
        "post": {
            "INSTALLED_APPS": ["dummyplugin"],
        }
    }
