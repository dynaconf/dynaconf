import pytest
from dynaconf import LazySettings
from dynaconf.loaders.yaml_loader import load

settings = LazySettings(
    DYNACONF_NAMESPACE='EXAMPLE',
)


YAML = """
example:
  host: server.com
  port: 8080
development:
  host: dev_server.com
"""

def test_load_from_yaml():
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    load(settings, filename=YAML, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=YAML)
    assert settings.HOST == 'server.com'


def test_no_filename_is_none():
    assert load(settings) is None


def test_error_on_invalid_namespace():
    with pytest.raises(KeyError):
        load(settings, filename=YAML, namespace='FOOBAR')


def test_load_single_key():
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
    load(settings, filename=YAML)
    yaml = """
    example:
       hello: world
    """
    settings.set('YAML', yaml)
    settings.execute_loaders(namespace='EXAMPLE')
    assert settings.HELLO == 'world'
