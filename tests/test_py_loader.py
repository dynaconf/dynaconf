import io
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
    with io.open(
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
    with io.open(
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
