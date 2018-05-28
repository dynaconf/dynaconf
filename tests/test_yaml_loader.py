import pytest
from dynaconf import LazySettings
from dynaconf.loaders.yaml_loader import load

settings = LazySettings(
    ENV_FOR_DYNACONF='PRODUCTION',
)


YAML = """
# the bellow is just to ensure `,` will not break string YAML
a: 'a,b'
default:
  password: 99999
  host: server.com
  port: 8080
  alist:
    - item1
    - item2
    - 23
  service:
    url: service.com
    port: 80
    auth:
      password: qwerty
      test: 1234
development:
  password: 88888
  host: devserver.com
production:
  password: 11111
  host: prodserver.com
global:
  global_value: global

"""

YAML2 = """
global:
  # @float casting not needed, used only for testing
  secret: '@float 42'
  password: 123456
  host: otheryaml.com
"""

YAMLS = [YAML, YAML2]


def test_load_from_yaml():
    """Assert loads from YAML string"""
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, env='DEVELOPMENT')
    assert settings.HOST == 'devserver.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'


def test_load_from_multiple_yaml():
    """Assert loads from YAML string"""
    load(settings, filename=YAMLS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAMLS, env='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'otheryaml.com'
    load(settings, filename=YAMLS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    load(settings, filename=YAML, env='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'devserver.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'
    assert settings.PASSWORD == 11111


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env():
    """Assert error raised if env is not found in YAML"""
    with pytest.raises(KeyError):
        load(settings, filename=YAML, env='FOOBAR', silent=False)


def test_no_key_error_on_invalid_env():
    """Assert error raised if env is not found in YAML"""
    load(settings, filename=YAML, env='FOOBAR', silent=True)


def test_load_single_key():
    """Test loading a single key"""
    yaml = """
    foo:
       bar: blaz
       zaz: naz
    """
    load(settings, filename=yaml, env='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False


def test_extra_yaml():
    """Test loading extra yaml file"""
    load(settings, filename=YAML)
    yaml = """
    example:
       helloexample: world
    """
    settings.set('YAML', yaml)
    settings.execute_loaders(env='EXAMPLE')
    assert settings.HELLOEXAMPLE == 'world'


def test_multi_extra_yaml():
    """Test loading extra yaml file"""
    load(settings, filename=YAMLS)
    yaml = """
    example:
       helloexample: world
    """
    yaml2 = """
    example:
       foo: bar
    """
    settings.set('YAML', [yaml, yaml2])
    settings.execute_loaders(env='EXAMPLE')
    assert settings.HELLOEXAMPLE == 'world'
    assert settings.FOO == 'bar'


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.yaml,b.yml,c.yaml,d.yml")


def test_cleaner():
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'
    assert settings.PORT == 8080
    assert settings.ALIST == ['item1', 'item2', 23]
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, env='DEVELOPMENT')
    assert settings.HOST == 'devserver.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'

    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOST == 'prodserver.com'


def test_using_env(tmpdir):
    load(settings, filename=YAML)
    assert settings.HOST == 'prodserver.com'

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.yaml")
    tmpfile.write(YAML)
    with settings.using_env('DEVELOPMENT', filename=str(tmpfile)):
        assert settings.HOST == 'devserver.com'
    assert settings.HOST == 'prodserver.com'
