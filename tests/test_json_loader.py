import pytest
from dynaconf import LazySettings
from dynaconf.loaders.json_loader import load

settings = LazySettings(
    ENV_FOR_DYNACONF='PRODUCTION',
)


JSON = """
{
    "a": "a,b",
    "default": {
        "password": "@int 99999",
        "host": "server.com",
        "port": "@int 8080",
        "alist": ["item1", "item2", 23],
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
        "password": "@int 88888",
        "host": "devserver.com"
    },
    "production": {
        "password": "@int 11111",
        "host": "prodserver.com"
    },
    "global": {
        "global_value": "global"
    }
}
"""

# the @float is not needed in JSON but kept to ensure it works
JSON2 = """
{
  "global": {
    "secret": "@float 42",
    "password": 123456,
    "host": "otherjson.com"
  }
}
"""

JSONS = [JSON, JSON2]


def test_load_from_json():
    """Assert loads from JSON string"""
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSON, env='DEVELOPMENT')
    assert settings.HOST == 'devserver.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'


def test_load_from_multiple_json():
    """Assert loads from JSON string"""
    load(settings, filename=JSONS)
    assert settings.HOST == 'otherjson.com'
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSONS, env='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'otherjson.com'
    load(settings, filename=JSONS)
    assert settings.HOST == 'otherjson.com'
    assert settings.PASSWORD == 123456
    load(settings, filename=JSON, env='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'devserver.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'
    assert settings.PASSWORD == 11111


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env():
    """Assert error raised if env is not found in JSON"""
    with pytest.raises(KeyError):
        load(settings, filename=JSON, env='FOOBAR', silent=False)


def test_no_key_error_on_invalid_env():
    """Assert error raised if env is not found in JSON"""
    load(settings, filename=JSON, env='FOOBAR', silent=True)


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
    load(settings, filename=_JSON, env='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.json,b.json,c.json,d.json")


def test_cleaner():
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=JSON, env='DEVELOPMENT')
    assert settings.HOST == 'devserver.com'
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'

    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOST == 'prodserver.com'


def test_using_env(tmpdir):
    load(settings, filename=JSON)
    assert settings.HOST == 'prodserver.com'

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.json")
    tmpfile.write(JSON)
    with settings.using_env('DEVELOPMENT', filename=str(tmpfile)):
        assert settings.HOST == 'devserver.com'
    assert settings.HOST == 'prodserver.com'
