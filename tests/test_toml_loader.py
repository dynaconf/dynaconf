from __future__ import annotations

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.toml_loader import encode_nulls
from dynaconf.loaders.toml_loader import load
from dynaconf.strategies.filtering import PrefixFilter

settings = LazySettings(environments=True, ENV_FOR_DYNACONF="PRODUCTION")


TOML = """
a = "a,b"
[default]
password = "@int 99999"
host = "server.com"
port = "@int 8080"
alist = [
  "item1",
  "item2",
  "@int 23"
]

  [default.service]
  url = "service.com"
  port = 80.0

    [default.service.auth]
    password = "qwerty"
    test = 1234.0

[development]
password = "@int 88888"
host = "devserver.com"

[production]
password = "@int 11111"
HOST = "prodserver.com"

[GLOBAL]
global_value = "global"
"""

TOML2 = """
[global]
secret = "@float 42"
password = 123456.0
host = "othertoml.com"
"""

INVALID_TOML_TO_BE_REMOVED_ON_4_0_0 = """
[global]
secret = "@float 42"
password = 123456.0
host = "othertoml.com"
emojis = "😀😀😀😀"
encoded_variable="This has accents like � and � � � � just to test encoding �"
# The above is not allowed by TOML, but it is allowed by Dynaconf < 4.0.0
"""


TOMLS = [TOML, TOML2]


def test_load_from_toml_with_invalid_unicode(tmpdir):
    # THIS TEST MUST FAIL AND BE REMOVED ON 4.0.0
    load(settings, filename=INVALID_TOML_TO_BE_REMOVED_ON_4_0_0)
    assert settings.ENCODED_VARIABLE == (
        "This has accents like � and � � � � just to test encoding �"
    )

    tmpfile = tmpdir.join("settings.toml")
    with open(tmpfile.strpath, "w", encoding="utf-8") as f:
        f.write(INVALID_TOML_TO_BE_REMOVED_ON_4_0_0)

    _settings = LazySettings(
        settings_files=[tmpfile.strpath], environments=True
    )
    assert _settings.ENCODED_VARIABLE == (
        "This has accents like � and � � � � just to test encoding �"
    )
    assert _settings.EMOJIS == "😀😀😀😀"


def test_load_from_toml():
    """Assert loads from TOML string"""
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=TOML, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"


def test_load_from_multiple_toml():
    """Assert loads from TOML string"""
    load(settings, filename=TOMLS)
    assert settings.HOST == "othertoml.com"
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=TOMLS, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "othertoml.com"
    load(settings, filename=TOMLS)
    assert settings.HOST == "othertoml.com"
    assert settings.PASSWORD == 123456
    load(settings, filename=TOML, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "devserver.com"
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"
    assert settings.PASSWORD == 11111


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env():
    """Assert error raised if env is not found in TOML"""
    with pytest.raises(KeyError):
        load(settings, filename=TOML, env="FOOBAR", silent=False)


def test_no_key_error_on_invalid_env():
    """Assert error raised if env is not found in TOML"""
    load(settings, filename=TOML, env="FOOBAR", silent=True)


def test_load_single_key():
    """Test loading a single key"""
    toml = """
    a = "a,b"
    [foo]
    bar = "blaz"
    ZAZ = "naz"
    lowerkey = 'hello'
    UPPERKEY = 'world'
    """
    load(settings, filename=toml, env="FOO", key="bar")
    assert settings.BAR == "blaz"
    assert settings.exists("BAR") is True
    assert settings.exists("ZAZ") is False
    load(settings, filename=toml, env="FOO", key="ZAZ")
    assert settings.ZAZ == "naz"
    load(settings, filename=toml, env="FOO", key="LOWERKEY")
    assert settings.LOWERKEY == "hello"
    load(settings, filename=toml, env="FOO", key="upperkey")
    assert settings.UPPERKEY == "world"


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.toml,b.tml,c.toml,d.tml")


def test_cleaner():
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=TOML, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"

    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOST == "prodserver.com"


def test_using_env(tmpdir):
    load(settings, filename=TOML)
    assert settings.HOST == "prodserver.com"

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.toml")
    tmpfile.write(TOML)
    with settings.using_env("DEVELOPMENT", filename=str(tmpfile)):
        assert settings.HOST == "devserver.com"
    assert settings.HOST == "prodserver.com"


def test_load_dunder():
    """Test load with dunder settings"""
    toml = """
    a = "a,b"
    [foo]
    colors__gray__code = '#CCCCCC'
    COLORS__gray__name = 'Gray'
    """
    load(settings, filename=toml, env="FOO")
    assert settings.COLORS.gray.code == "#CCCCCC"
    assert settings.COLORS.gray.name == "Gray"


def test_encode_nulls():
    assert encode_nulls(None) == "@none "
    assert encode_nulls([None, None]) == ["@none ", "@none "]
    assert encode_nulls((None, None)) == ["@none ", "@none "]
    assert encode_nulls({"nullable": None}) == {"nullable": "@none "}
    assert encode_nulls(1) == 1
    assert encode_nulls(1.1) == 1.1
    assert encode_nulls(True) is True
    assert encode_nulls(False) is False
    assert encode_nulls("") == ""
    assert encode_nulls("text") == "text"


def test_envless():
    settings = LazySettings()
    ini = """
    a = "a,b"
    colors__white__code = '#FFFFFF'
    COLORS__white__name = 'white'
    """
    load(settings, filename=ini)
    assert settings.a == "a,b"
    assert settings.COLORS.white.code == "#FFFFFF"
    assert settings.COLORS.white.name == "white"


def test_prefix():
    settings = LazySettings(filter_strategy=PrefixFilter("prefix"))
    ini = """
    prefix_a = "a,b"
    prefix_colors__white__code = '#FFFFFF'
    COLORS__white__name = 'white'
    """
    load(settings, filename=ini)
    assert settings.a == "a,b"
    assert settings.COLORS.white.code == "#FFFFFF"
    with pytest.raises(AttributeError):
        settings.COLORS.white.name
