from __future__ import annotations

import os
import sys
from collections import OrderedDict
from os import environ

import pytest

from dynaconf import settings  # noqa
from dynaconf.loaders.env_loader import load
from dynaconf.loaders.env_loader import load_from_env
from dynaconf.loaders.env_loader import write

# GLOBAL ENV VARS
environ["DYNACONF_HOSTNAME"] = "host.com"
environ["DYNACONF_PORT"] = "@int 5000"
environ["DYNACONF_ALIST"] = '@json ["item1", "item2", "item3", 123]'
environ["DYNACONF_ADICT"] = '@json {"key": "value", "int": 42}'
environ["DYNACONF_DEBUG"] = "@bool true"
environ["DYNACONF_MUSTBEFRESH"] = "first"
environ["DYNACONF_MUSTBEALWAYSFRESH"] = "first"
environ["DYNACONF_SHOULDBEFRESHINCONTEXT"] = "first"
environ["DYNACONF_VALUE"] = "@float 42.1"

# environ['FRESH_VARS_FOR_DYNACONF'] = '@json ["MUSTBEALWAYSFRESH"]'
# settings.configure(IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF=True)
settings.configure(
    FRESH_VARS_FOR_DYNACONF=["MUSTBEALWAYSFRESH"],
    ROOT_PATH_FOR_DYNACONF=os.path.dirname(os.path.abspath(__file__)),
)

SETTINGS_DATA = OrderedDict()
# Numbers
SETTINGS_DATA["DYNACONF_INTEGER"] = 42
SETTINGS_DATA["DYNACONF_FLOAT"] = 3.14
# Text
# 'DYNACONF_STRING': Hello,
SETTINGS_DATA["DYNACONF_STRING2"] = "Hello"
SETTINGS_DATA["DYNACONF_STRING2_LONG"] = "Hello World!"
SETTINGS_DATA["DYNACONF_BOOL"] = True
SETTINGS_DATA["DYNACONF_BOOL2"] = False
# Use extra quotes to force a string from other type
SETTINGS_DATA["DYNACONF_STRING21"] = '"42"'
SETTINGS_DATA["DYNACONF_STRING22"] = "'true'"
# Arrays must be homogeneous in toml syntax
SETTINGS_DATA["DYNACONF_ARRAY"] = [1, 2, 3]
SETTINGS_DATA["DYNACONF_ARRAY2"] = [1.1, 2.2, 3.3]
SETTINGS_DATA["DYNACONF_ARRAY3"] = ["a", "b", "c"]
# Dictionaries
SETTINGS_DATA["DYNACONF_DICT"] = {"val": 123}

SETTINGS_DATA_GROUND_TRUTH = """DYNACONF_TESTING=true
DYNACONF_INTEGER=42
DYNACONF_FLOAT=3.14
DYNACONF_STRING2=Hello
DYNACONF_STRING2_LONG="Hello World!"
DYNACONF_BOOL=True
DYNACONF_BOOL2=False
DYNACONF_STRING21="42"
DYNACONF_STRING22="true"
DYNACONF_ARRAY="[1, 2, 3]"
DYNACONF_ARRAY2="[1.1, 2.2, 3.3]"
DYNACONF_ARRAY3="[\'a\', \'b\', \'c\']"
DYNACONF_DICT="{\'val\': 123}"
"""


def test_write(tmpdir):
    settings_path = tmpdir.join(".env")

    write(settings_path, SETTINGS_DATA)

    ground_truth = SETTINGS_DATA_GROUND_TRUTH.split("\n")

    with open(str(settings_path)) as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines):
            line = line.strip()
            if line.split("=")[0] == "DYNACONF_TESTING":
                continue  # this key is written by the test itself; skip.
            assert line == ground_truth[idx].strip()


def test_env_loader():
    assert settings.HOSTNAME == "host.com"
    assert settings.PORT == 5000
    assert settings.ALIST == ["item1", "item2", "item3", 123]
    assert settings.ADICT == {"key": "value", "int": 42}


def test_single_key():
    environ["DYNACONF_HOSTNAME"] = "changedhost.com"
    load(settings, key="HOSTNAME")
    # hostname is reloaded
    assert settings.HOSTNAME == "changedhost.com"


def test_dotenv_loader():
    assert settings.DOTENV_INT == 1
    assert settings.DOTENV_STR == "hello"
    assert settings.DOTENV_FLOAT == 4.2
    assert settings.DOTENV_BOOL is False
    assert settings.DOTENV_JSON == ["1", "2"]
    assert settings.DOTENV_NOTE is None


def test_get_fresh():
    assert settings.MUSTBEFRESH == "first"
    environ["DYNACONF_MUSTBEFRESH"] = "second"
    with pytest.raises(AssertionError):
        # fresh should now be second
        assert settings.exists("MUSTBEFRESH")
        assert settings.get_fresh("MUSTBEFRESH") == "first"
    assert settings.get_fresh("MUSTBEFRESH") == "second"

    environ["DYNACONF_THISMUSTEXIST"] = "@int 1"
    # must tnot exist yet (not loaded)
    assert settings.exists("THISMUSTEXIST") is False
    # must exist because fresh will call loaders
    assert settings.exists("THISMUSTEXIST", fresh=True) is True
    # loaders run only once
    assert settings.get("THISMUSTEXIST") == 1

    environ["DYNACONF_THISMUSTEXIST"] = "@int 23"
    del environ["DYNACONF_THISMUSTEXIST"]
    # this should error because envvar got cleaned
    # but it is not, so cleaners should be fixed
    assert settings.get_fresh("THISMUSTEXIST") is None
    with pytest.raises(AttributeError):
        settings.THISMUSTEXIST
    with pytest.raises(KeyError):
        settings["THISMUSTEXIST"]

    environ["DYNACONF_THISMUSTEXIST"] = "@int 23"
    load(settings)
    assert settings.get("THISMUSTEXIST") == 23


def test_always_fresh():
    # assert environ['FRESH_VARS_FOR_DYNACONF'] == '@json ["MUSTBEALWAYSFRESH"]'  # noqa
    assert settings.FRESH_VARS_FOR_DYNACONF == ["MUSTBEALWAYSFRESH"]
    assert settings.MUSTBEALWAYSFRESH == "first"
    environ["DYNACONF_MUSTBEALWAYSFRESH"] = "second"
    assert settings.MUSTBEALWAYSFRESH == "second"
    environ["DYNACONF_MUSTBEALWAYSFRESH"] = "third"
    assert settings.MUSTBEALWAYSFRESH == "third"


def test_fresh_context():
    assert settings.SHOULDBEFRESHINCONTEXT == "first"
    environ["DYNACONF_SHOULDBEFRESHINCONTEXT"] = "second"
    assert settings.SHOULDBEFRESHINCONTEXT == "first"
    with settings.fresh():
        assert settings.get("DOTENV_INT") == 1
        assert settings.SHOULDBEFRESHINCONTEXT == "second"


def test_cleaner():
    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOSTNAME == "host.com"


def test_empty_string_prefix():
    environ["_VALUE"] = "underscored"
    load_from_env(
        identifier="env_global", key=None, prefix="", obj=settings, silent=True
    )
    assert settings.VALUE == "underscored"


def test_no_prefix():
    environ["VALUE"] = "no_prefix"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix=False,
        obj=settings,
        silent=True,
    )
    assert settings.VALUE == "no_prefix"


def test_none_as_string_prefix():
    environ["NONE_VALUE"] = "none as prefix"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="none",
        obj=settings,
        silent=True,
    )
    assert settings.VALUE == "none as prefix"


def test_backwards_compat_using_env_argument():
    environ["BLARG_VALUE"] = "BLARG as prefix"
    load_from_env(
        identifier="env_global",
        key=None,
        env="BLARG",  # renamed to `prefix` on 3.0.0
        obj=settings,
        silent=True,
    )
    assert settings.VALUE == "BLARG as prefix"


def test_load_signed_integer():
    environ["799_SIGNED_NEG_INT"] = "-1"
    environ["799_SIGNED_POS_INT"] = "+1"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="799",
        obj=settings,
        silent=True,
    )
    assert settings.SIGNED_NEG_INT == -1
    assert settings.SIGNED_POS_INT == 1


def test_env_is_not_str_raises():
    with pytest.raises(TypeError):
        load_from_env(settings, prefix=int)
    with pytest.raises(TypeError):
        load_from_env(settings, prefix=True)


def test_can_load_in_to_dict():
    os.environ["LOADTODICT"] = "true"
    sets = {}
    load_from_env(sets, prefix=False, key="LOADTODICT")
    assert sets["LOADTODICT"] is True


def clean_environ(prefix):
    keys = [k for k in environ if k.startswith(prefix)]
    for key in keys:
        environ.pop(key)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Windows env vars are case insensitive",
)
def test_load_dunder(clean_env):
    """Test load and merge with dunder settings"""
    clean_environ("DYNACONF_DATABASES")
    settings.set(
        "DATABASES",
        {
            "default": {
                "NAME": "db",
                "ENGINE": "module.foo.engine",
                "ARGS": {"timeout": 30},
                "PORTS": [123, 456],
            }
        },
    )
    # change engine
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ENGINE"] = "other.module"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default.ENGINE == "other.module"

    # change timeout directly
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ARGS__timeout"] = "99"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default.ARGS.timeout == 99

    # add to ARGS
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ARGS"] = "@merge {retries=10}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default.ARGS.retries == 10
    assert settings.DATABASES.default.ARGS.timeout == 99

    # Ensure dictionary keeps its format
    assert settings.DATABASES == {
        "default": {
            "NAME": "db",
            "ENGINE": "other.module",
            "ARGS": {"timeout": 99, "retries": 10},
            "PORTS": [123, 456],
        }
    }
    assert "default" in settings["DATABASES"].keys()
    assert "DEFAULT" not in settings["DATABASES"].keys()
    assert "NAME" in settings["DATABASES"]["default"].keys()
    assert "name" not in settings["DATABASES"]["default"].keys()

    # Clean args
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ARGS"] = "{timeout=8}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default.ARGS == {"timeout": 8}

    # Make args empty
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ARGS"] = "{}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default.ARGS == {}

    # Remove ARGS key
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__ARGS"] = "@del"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert "ARGS" not in settings.DATABASES.default.keys()

    # add to existing PORTS
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__PORTS"] = "@merge [789, 101112]"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert "ARGS" not in settings.DATABASES.default.keys()
    assert settings.DATABASES.default.PORTS == [123, 456, 789, 101112]

    # reset PORTS
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__PORTS"] = "[789, 101112]"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert "ARGS" not in settings.DATABASES.default.keys()
    assert settings.DATABASES.default.PORTS == [789, 101112]

    # delete PORTS
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default__PORTS"] = "@del"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert "ARGS" not in settings.DATABASES.default.keys()
    assert "PORTS" not in settings.DATABASES.default.keys()

    # reset default key
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default"] = "{}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES.default == {}

    # remove default
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__default"] = "@del"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES == {}

    # set value to databases
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES__foo"] = "bar"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES == {"foo": "bar"}

    # reset databases
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES"] = "{hello='world'}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES == {"hello": "world"}

    # also reset databases
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES"] = "{yes='no'}"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert settings.DATABASES == {"yes": "no"}

    # remove databases
    clean_environ("DYNACONF_DATABASES")
    environ["DYNACONF_DATABASES"] = "@del"
    load_from_env(
        identifier="env_global",
        key=None,
        prefix="dynaconf",
        obj=settings,
        silent=True,
    )
    assert "DATABASES" not in settings


def test_filtering_unknown_variables():
    # Predefine some known variable.
    settings.MYCONFIG = "bar"
    # Enable environment filtering.
    settings.IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF = True

    # Pollute the environment.
    environ["IGNOREME"] = "foo"

    load_from_env(
        obj=settings,
        prefix=False,
        key=None,
        silent=True,
        identifier="env_global",
        env=False,
    )

    # Verify the filter works.
    assert not settings.get("IGNOREME")
    # Smoke test.
    assert settings.get("MYCONFIG") == "bar"


def test_filtering_unknown_variables_with_prefix():
    # Predefine some known variable.
    settings.MYCONFIG = "bar"
    # Enable environment filtering.
    settings.IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF = True

    # Pollute the environment.
    environ["APP_IGNOREME"] = "foo"
    # Also change legitimate variable.
    environ["APP_MYCONFIG"] = "ham"

    load_from_env(
        obj=settings,
        prefix="APP",
        key=None,
        silent=True,
        identifier="env_global",
        env=False,
    )

    # Verify the filter works.
    assert not settings.get("IGNOREME")
    # Smoke test.
    assert settings.get("MYCONFIG") == "ham"
