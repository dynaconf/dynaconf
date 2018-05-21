import pytest
from dynaconf import LazySettings
from dynaconf.loaders.ini_loader import load, clean

settings = LazySettings(
    NAMESPACE_FOR_DYNACONF='EXAMPLE',
)


INI = """
[example]
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
host = "dev_server.com"
"""

INI2 = """
[example]
secret = "@float 42"
password = '@int 123456'
host = "otheryaml.com"
"""

INIS = [INI, INI2]


def test_load_from_ini():
    """Assert loads from INI string"""
    load(settings, filename=INI)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INI, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=INI)
    assert settings.HOST == 'server.com'


def test_load_from_multiple_ini():
    """Assert loads from INI string"""
    load(settings, filename=INIS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INIS, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'otheryaml.com'
    load(settings, filename=INIS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    load(settings, filename=INI, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=INI)
    assert settings.HOST == 'server.com'
    assert settings.PASSWORD == 99999


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in INI"""
    with pytest.raises(KeyError):
        load(settings, filename=INI, namespace='FOOBAR', silent=False)


def test_no_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in INI"""
    load(settings, filename=INI, namespace='FOOBAR', silent=True)


def test_load_single_key():
    """Test loading a single key"""
    ini = """
    [foo]
    bar = "blaz"
    zaz = "naz"
    """
    load(settings, filename=ini, namespace='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.ini,b.ini,c.conf,d.properties")


def test_cleaner():
    load(settings, filename=INI)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=INI, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=INI)
    assert settings.HOST == 'server.com'

    clean(settings, settings.namespace)
