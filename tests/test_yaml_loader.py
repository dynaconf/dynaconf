import os

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.yaml_loader import load

settings = LazySettings(
    environments=True,
    ENV_FOR_DYNACONF="PRODUCTION",
    ROOT_PATH_FOR_DYNACONF=os.path.dirname(os.path.abspath(__file__)),
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
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"


def test_load_from_multiple_yaml():
    """Assert loads from YAML string"""
    load(settings, filename=YAMLS)
    assert settings.HOST == "otheryaml.com"
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAMLS, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "otheryaml.com"
    load(settings, filename=YAMLS)
    assert settings.HOST == "otheryaml.com"
    assert settings.PASSWORD == 123456
    load(settings, filename=YAML, env="DEVELOPMENT")
    assert settings.PORT == 8080
    assert settings.HOST == "devserver.com"
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"
    assert settings.PASSWORD == 11111


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env():
    """Assert error raised if env is not found in YAML"""
    with pytest.raises(KeyError):
        load(settings, filename=YAML, env="FOOBAR", silent=False)


def test_no_key_error_on_invalid_env():
    """Assert error raised if env is not found in YAML"""
    load(settings, filename=YAML, env="FOOBAR", silent=True)


def test_load_single_key():
    """Test loading a single key"""
    yaml = """
    foo:
       bar: blaz
       zaz: naz
    """
    load(settings, filename=yaml, env="FOO", key="bar")
    assert settings.BAR == "blaz"
    assert settings.exists("BAR") is True
    assert settings.exists("ZAZ") is False


def test_extra_yaml():
    """Test loading extra yaml file"""
    load(settings, filename=YAML)
    yaml = """
    example:
       helloexample: world
    """
    settings.set("YAML", yaml)
    settings.execute_loaders(env="EXAMPLE")
    assert settings.HELLOEXAMPLE == "world"


def test_empty_value():
    load(settings, filename="")


def test_multiple_filenames():
    load(settings, filename="a.yaml,b.yml,c.yaml,d.yml")


def test_cleaner():
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"
    assert settings.PORT == 8080
    assert settings.ALIST == ["item1", "item2", 23]
    assert settings.SERVICE["url"] == "service.com"
    assert settings.SERVICE.url == "service.com"
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == "qwerty"
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=YAML, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"

    settings.clean()
    with pytest.raises(AttributeError):
        assert settings.HOST == "prodserver.com"


def test_using_env(tmpdir):
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.yaml")
    tmpfile.write(YAML)
    with settings.using_env("DEVELOPMENT", filename=str(tmpfile)):
        assert settings.HOST == "devserver.com"
    assert settings.HOST == "prodserver.com"


def test_load_dunder():
    """Test load with dunder settings"""
    yaml = """
    foo:
       bar: blaz
       zaz: naz
       colors__black__code: '#000000'
       COLORS__black__name: Black
    """
    load(settings, filename=yaml, env="FOO")
    assert settings.COLORS.black.code == "#000000"
    assert settings.COLORS.black.name == "Black"


def test_local_files(tmpdir):

    settings_file_yaml = """
    default:
      name: Bruno
      colors:
        - green
        - blue
      data:
        link: brunorocha.org
      other:
        foo: bar
      music:
        current:
          volume: 10
          title: The Beatles - Strawberry Fields
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)

    local_file_yaml = """
    default:
      name: Bruno Rocha
      colors:
        - red
        - dynaconf_merge
      data:
        city: Guarulhos
        dynaconf_merge: true
      other:
        baz: zaz
      music__current__volume: 100
      music__current__title: Led Zeppelin - Immigrant Song
    """
    tmpdir.join("settings.local.yaml").write(local_file_yaml)

    conf = LazySettings(environments=True, settings_file="settings.yaml")
    assert conf.NAME == "Bruno Rocha"
    assert set(conf.COLORS) == set(["red", "green", "blue"])
    assert conf.DATA.link == "brunorocha.org"
    assert conf.DATA.city == "Guarulhos"
    assert conf.OTHER == {"baz": "zaz"}
    assert conf.MUSIC.current.volume == 100
    assert conf.MUSIC.current.title == "Led Zeppelin - Immigrant Song"


def test_explicit_local_files(tmpdir):

    settings_file_yaml = """
    default:
      name: Bruno
      colors:
        - green
        - blue
      data:
        link: brunorocha.org
      other:
        foo: bar
      music:
        current:
          volume: 10
          title: The Beatles - Strawberry Fields
    """
    tmpdir.join("foo.yaml").write(settings_file_yaml)

    local_file_yaml = """
    default:
      name: Bruno Rocha
      colors:
        - red
        - dynaconf_merge
      data:
        city: Guarulhos
        dynaconf_merge: true
      other:
        baz: zaz
      music__current__volume: 100
      music__current__title: Led Zeppelin - Immigrant Song
      music__current__even__inner__element: true
    """
    tmpdir.join("foo.local.yaml").write(local_file_yaml)

    conf = LazySettings(
        environments=True,
        SETTINGS_FILE_FOR_DYNACONF=["foo.yaml", "foo.local.yaml"],
    )

    assert conf.NAME == "Bruno Rocha"
    assert set(conf.COLORS) == set(["red", "green", "blue"])
    assert conf.DATA.link == "brunorocha.org"
    assert conf.DATA.city == "Guarulhos"
    assert conf.OTHER == {"baz": "zaz"}
    assert conf.MUSIC.current.volume == 100
    assert conf.MUSIC.current.title == "Led Zeppelin - Immigrant Song"
    assert conf.get("music.current.even.inner.element") is True


def test_envless():
    settings = LazySettings()
    _yaml = """
    a: a,b
    colors__white__code: "#FFFFFF"
    COLORS__white__name: "white"
    """
    load(settings, filename=_yaml)
    assert settings.a == "a,b"
    assert settings.COLORS.white.code == "#FFFFFF"
    assert settings.COLORS.white.name == "white"


def test_empty_env():
    settings = LazySettings(environments=True)
    _yaml = """
    default:
        foo: bar
    development:
    """
    load(settings, filename=_yaml)
    assert settings.FOO == "bar"


def test_empty_env_from_file(tmpdir):
    """Assert empty env is not crashing on load."""
    settings_file_yaml = """
    default:
        foo: bar
    development: ~
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(environments=True, settings_file="settings.yaml")
    settings.reload()
    assert settings.FOO == "bar"
