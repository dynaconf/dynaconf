from __future__ import annotations

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.ini_loader import load
from dynaconf.strategies.filtering import PrefixFilter

settings = LazySettings(environments=True, ENV_FOR_DYNACONF="PRODUCTION")


INI = """
a = 'a,b'
[default]
password = '@int 99999'
host = "server.com"
port = '@int 8080'
alist = item1, item2, '@int 23'

  [[service]]
  url = "service.com"
  port = '@int 80'

    [[[auth]]]
    password = "qwerty"
    test = '@int 1234'

[development]
password = '@int 88888'
host = "devserver.com"

[production]
password = '@int 11111'
host = "prodserver.com"

[global]
global_value = 'global'
"""

INI2 = """
[global]
secret = "@float 42"
password = '@int 123456'
host = "otherini.com"
"""

INIS = [INI, INI2]


def test_load_from_ini():
    """Assert loads from INI string"""
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INI, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080


def test_load_from_multiple_ini():
    """Assert loads from INI string"""
    load(settings, filename=INIS)
    assert settings.HOST == "otherini.com"
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INIS, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "otherini.com"
    load(settings, filename=INIS)
    assert settings.HOST == "otherini.com"
    assert settings.PASSWORD == 123456
    load(settings, filename=INI, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "devserver.com"
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"
    assert settings.PASSWORD == 11111


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env():
    """Assert error raised if env is not found in INI"""
    with pytest.raises(KeyError):
        load(settings, filename=INI, env="FOOBAR", silent=False)


def test_no_key_error_on_invalid_env():
    """Assert error raised if env is not found in INI"""
    load(settings, filename=INI, env="FOOBAR", silent=True)


def test_load_single_key():
    """Test loading a single key"""
    ini = """
    a = "a,b"
    [foo]
    bar = "blaz"
    ZAZ = "naz"
    lowerkey = 'hello'
    UPPERKEY = 'world'
    """
    load(settings, filename=ini, env="FOO", key="bar")
    assert settings.BAR == "blaz"
    assert settings.exists("BAR") is True
    assert settings.exists("ZAZ") is False
    load(settings, filename=ini, env="FOO", key="ZAZ")
    assert settings.ZAZ == "naz"
    load(settings, filename=ini, env="FOO", key="LOWERKEY")
    assert settings.LOWERKEY == "hello"
    load(settings, filename=ini, env="FOO", key="upperkey")
    assert settings.UPPERKEY == "world"


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.ini,b.ini,c.conf,d.properties")


def test_cleaner():
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INI, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"

    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOST == "prodserver.com"


def test_using_env(tmpdir):
    load(settings, filename=INI)
    assert settings.HOST == "prodserver.com"

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.ini")
    tmpfile.write(INI)
    with settings.using_env("DEVELOPMENT", filename=str(tmpfile)):
        assert settings.HOST == "devserver.com"
    assert settings.HOST == "prodserver.com"


def test_load_dunder():
    """Test load with dunder settings"""
    ini = """
    a = "a,b"
    [foo]
    colors__white__code = '#FFFFFF'
    COLORS__white__name = 'white'
    """
    load(settings, filename=ini, env="FOO")
    assert settings.COLORS.white.code == "#FFFFFF"
    assert settings.COLORS.white.name == "white"


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
