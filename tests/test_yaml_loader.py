import pytest
from dynaconf import LazySettings
from dynaconf.loaders.yaml_loader import load, clean

settings = LazySettings(
    NAMESPACE_FOR_DYNACONF='EXAMPLE',
)


YAML = """
# the bellow is just to ensure `,` will not break string YAML
a: "a,b"
example:
  password: 99999
  host: server.com
  port: 8080
  service:
    url: service.com
    port: 80
    auth:
        password: qwerty
        test: 1234
development:
  password: 88888
  host: dev_server.com
"""

YAML2 = """
example:
  # @float casting not needed, used only for testing
  secret: '@float 42'
  password: 123456
  host: otheryaml.com
"""

YAMLS = [YAML, YAML2]


def test_load_from_yaml():
    """Assert loads from YAML string"""
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'


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
    load(settings, filename=YAMLS, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'otheryaml.com'
    load(settings, filename=YAMLS)
    assert settings.HOST == 'otheryaml.com'
    assert settings.PASSWORD == 123456
    load(settings, filename=YAML, namespace='DEVELOPMENT')
    assert settings.PORT == 8080
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'
    assert settings.PASSWORD == 99999

def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in YAML"""
    with pytest.raises(KeyError):
        load(settings, filename=YAML, namespace='FOOBAR', silent=False)


def test_no_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in YAML"""
    load(settings, filename=YAML, namespace='FOOBAR', silent=True)


def test_load_single_key():
    """Test loading a single key"""
    yaml = """
    foo:
       bar: blaz
       zaz: naz
    """
    load(settings, filename=yaml, namespace='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False


def test_extra_yaml():
    """Test loading extra yaml file"""
    load(settings, filename=YAML)
    yaml = """
    example:
       hello: world
    """
    settings.set('YAML', yaml)
    settings.execute_loaders(namespace='EXAMPLE')
    assert settings.HELLO == 'world'


def test_multi_extra_yaml():
    """Test loading extra yaml file"""
    load(settings, filename=YAMLS)
    yaml = """
    example:
       hello: world
    """
    yaml2 = """
    example:
       foo: bar
    """
    settings.set('YAML', [yaml, yaml2])
    settings.execute_loaders(namespace='EXAMPLE')
    assert settings.HELLO == 'world'
    assert settings.FOO == 'bar'


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.yaml,b.yml,c.yaml,d.yml")


def test_cleaner():
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'
    clean(settings, settings.namespace)
