import pytest
from dynaconf import LazySettings
from dynaconf.loaders.json_loader import load, clean

settings = LazySettings(
    NAMESPACE_FOR_DYNACONF='EXAMPLE',
)


JSON = """
{
  "a": "a,b",
  "example": {
    "password": 99999,
    "host": "server.com",
    "port": 8080,
    "service": {
      "url": "service.com",
      "port": 80,
      "auth": {
        "password": "qwerty",
        "test": 1234
      }
    }
  },
  "development": {
    "password": 88888,
    "host": "dev_server.com"
  }
}
"""

# the @float is not needed in JSON but kept to ensure it works
JSON2 = """
{
  "example": {
    "secret": "@float 42",
    "password": 123456,
    "host": "otheryaml.com"
  }
}
"""

JSONS = [JSON, JSON2]


def test_load_from_json():
    """Assert loads from JSON string"""
    load(settings, filename=JSON)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSON, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'server.com'


def test_load_from_multiple_json():
    """Assert loads from JSON string"""
    load(settings, filename=JSONS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSONS, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'otheryaml.com'
    load(settings, filename=JSONS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    load(settings, filename=JSON, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'server.com'
    assert settings.PASSWORD == 99999


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in JSON"""
    with pytest.raises(KeyError):
        load(settings, filename=JSON, namespace='FOOBAR', silent=False)


def test_no_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in JSON"""
    load(settings, filename=JSON, namespace='FOOBAR', silent=True)


def test_load_single_key():
    """Test loading a single key"""
    _JSON = """
    {
      "foo": {
        "bar": "blaz",
        "zaz": "naz"
      }
    }
    """
    load(settings, filename=_JSON, namespace='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.json,b.json,c.json,d.json")


def test_cleaner():
    load(settings, filename=JSON)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSON, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'server.com'
    clean(settings, settings.namespace)
