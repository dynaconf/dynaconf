from __future__ import annotations

import os

import pytest

from dynaconf import LazySettings
from dynaconf.loaders.yaml_loader import load
from dynaconf.strategies.filtering import PrefixFilter


@pytest.fixture(scope="module")
def settings():
    return LazySettings(
        environments=True,
        ENV_FOR_DYNACONF="PRODUCTION",
        # ROOT_PATH_FOR_DYNACONF=os.path.dirname(os.path.abspath(__file__)),
    )


YAML = """
# the below is just to ensure `,` will not break string YAML
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
  spaced key: 1
  spaced nested:
    key: 1
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


def test_load_from_yaml(settings):
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
    assert settings.spaced_key == 1
    assert settings.spaced_nested.key == 1
    assert settings.spaced_nested["key"] == 1
    assert settings["spaced key"] == 1
    assert settings["SPACED KEY"] == 1
    load(settings, filename=YAML, env="DEVELOPMENT")
    assert settings.HOST == "devserver.com"
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"


def test_load_from_multiple_yaml(settings):
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


def test_no_filename_is_none(settings):
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_env(settings):
    """Assert error raised if env is not found in YAML"""
    with pytest.raises(KeyError):
        load(settings, filename=YAML, env="FOOBAR", silent=False)


def test_no_key_error_on_invalid_env(settings):
    """Assert error raised if env is not found in YAML"""
    load(settings, filename=YAML, env="FOOBAR", silent=True)


def test_load_single_key(settings):
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


def test_extra_yaml(settings):
    """Test loading extra yaml file"""
    load(settings, filename=YAML)
    yaml = """
    example:
       helloexample: world
    """
    settings.set("YAML", yaml)
    settings.execute_loaders(env="EXAMPLE")
    assert settings.HELLOEXAMPLE == "world"


def test_empty_value(settings):
    load(settings, filename="")


def test_multiple_filenames(settings):
    load(settings, filename="a.yaml,b.yml,c.yaml,d.yml")


def test_cleaner(settings):
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


def test_using_env(tmpdir, settings):
    load(settings, filename=YAML)
    assert settings.HOST == "prodserver.com"

    tmpfile = tmpdir.mkdir("sub").join("test_using_env.yaml")
    tmpfile.write(YAML)
    with settings.using_env("DEVELOPMENT", filename=str(tmpfile)):
        assert settings.HOST == "devserver.com"
    assert settings.HOST == "prodserver.com"


def test_load_dunder(settings):
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
    assert set(conf.COLORS) == {"red", "green", "blue"}
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
    assert set(conf.COLORS) == {"red", "green", "blue"}
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


def test_prefix():
    settings = LazySettings(filter_strategy=PrefixFilter("prefix"))
    _yaml = """
    prefix_a: a,b
    prefix_colors__white__code: "#FFFFFF"
    COLORS__white__name: "white"
    """
    load(settings, filename=_yaml)
    assert settings.a == "a,b"
    assert settings.COLORS.white.code == "#FFFFFF"
    with pytest.raises(AttributeError):
        settings.COLORS.white.name


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


def test_merge_unique_in_a_first_level(tmpdir):
    """Assert merge unique in a first level."""
    settings_file_yaml = """
    default:
        colors: "@merge_unique green,blue"
        non_exist: "@merge_unique item1,item2"
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(
        environments=True,
        settings_file="settings.yaml",
        COLORS=["red", "green"],
    )
    settings.reload()
    assert settings.COLORS == ["red", "green", "blue"]
    assert settings.NON_EXIST == ["item1", "item2"]


def test_should_not_merge_if_merge_is_not_explicit_set(tmpdir):
    """Should not merge if merge is not explicit set."""
    settings_file_yaml = """
    default:
      SOME_KEY: "value"
      SOME_LIST:
        - "item_1"
        - "item_2"
        - "item_3"
    other:
      SOME_KEY: "new_value"
      SOME_LIST:
        - "item_4"
        - "item_5"
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(
        environments=True,
        settings_files=["settings.yaml"],
    )
    settings.reload()
    assert settings.SOME_KEY == "value"
    assert settings.SOME_LIST == ["item_1", "item_2", "item_3"]

    other_settings = settings.from_env("other")
    assert other_settings.SOME_KEY == "new_value"
    assert other_settings.SOME_LIST == ["item_4", "item_5"]


def test_should_not_duplicate_with_global_merge(tmpdir):
    """Assert merge unique in a first level. Issue #653"""
    settings_file_yaml = """
    default:
      SOME_KEY: "value"
      SOME_LIST:
        - "item_1"
        - "item_2"
        - "item_3"
    other:
      SOME_KEY: "new_value"
      SOME_LIST:
        - "item_4"
        - "item_5"
    even_other:
      SOME_KEY: "new_value_2"
      SOME_LIST:
        - "item_6"
        - "item_7"
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(
        environments=True, settings_files=["settings.yaml"], merge_enabled=True
    )
    # settings.reload()
    assert settings.SOME_KEY == "value"
    assert settings.SOME_LIST == ["item_1", "item_2", "item_3"]

    other_settings = settings.from_env("other")
    assert other_settings.SOME_KEY == "new_value"
    assert other_settings.SOME_LIST == [
        "item_1",
        "item_2",
        "item_3",
        "item_4",
        "item_5",
    ]


def test_should_duplicate_when_explicit_set(tmpdir):
    """Issue #653"""
    settings_file_yaml = """
    default:
      SCRIPTS:
        - "script1.sh"
        - "script2.sh"
        - "script3.sh"
    other:
      SCRIPTS:
        - "script4.sh"
        - "script1.sh"
        - "dynaconf_merge"
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(
        environments=True, settings_files=["settings.yaml"]
    )
    assert settings.SCRIPTS == [
        "script1.sh",
        "script2.sh",
        "script3.sh",
    ]

    other_settings = settings.from_env("other")
    assert other_settings.SCRIPTS == [
        "script1.sh",
        "script2.sh",
        "script3.sh",
        "script4.sh",
        "script1.sh",  # explicit wants to duplicate
    ]


def test_should_NOT_duplicate_when_explicit_set(tmpdir):
    """Issue #653"""
    settings_file_yaml = """
    default:
      SCRIPTS:
        - "script1.sh"
        - "script2.sh"
        - "script3.sh"
    other:
      SCRIPTS:
        - "script4.sh"
        - "script1.sh"
        - "dynaconf_merge_unique"  # NO DUPLICATE
    """
    tmpdir.join("settings.yaml").write(settings_file_yaml)
    settings = LazySettings(
        environments=True, settings_files=["settings.yaml"]
    )
    assert settings.SCRIPTS == [
        "script1.sh",
        "script2.sh",
        "script3.sh",
    ]

    other_settings = settings.from_env("other")
    assert other_settings.SCRIPTS == [
        "script2.sh",
        "script3.sh",
        "script4.sh",
        "script1.sh",
        # merge_unique does not duplicate, but overrides the order
    ]


def test_empty_yaml_key_overriding(tmpdir):
    new_key_value = "new_key_value"
    os.environ["DYNACONF_LEVEL1__KEY"] = new_key_value
    os.environ["DYNACONF_LEVEL1__KEY2"] = new_key_value
    os.environ["DYNACONF_LEVEL1__key3"] = new_key_value
    os.environ["DYNACONF_LEVEL1__KEY4"] = new_key_value
    os.environ["DYNACONF_LEVEL1__KEY5"] = new_key_value

    tmpdir.join("test.yml").write(
        """
        level1:
          key: key_value
          KEY2:
          key3:
          keY4:
        """
    )

    for merge_state in (True, False):
        _settings = LazySettings(
            settings_files=["test.yml"], merge_enabled=merge_state
        )
        assert _settings.level1.key == new_key_value
        assert _settings.level1.key2 == new_key_value
        assert _settings.level1.key3 == new_key_value
        assert _settings.level1.get("KEY4") == new_key_value
        assert _settings.level1.get("key4") == new_key_value
        assert _settings.level1.get("keY4") == new_key_value
        assert _settings.level1.get("keY6", "foo") == "foo"
        assert _settings.level1.get("KEY6", "bar") == "bar"
        assert _settings.level1["Key4"] == new_key_value
        assert _settings.level1.Key4 == new_key_value
        assert _settings.level1.KEy4 == new_key_value
        assert _settings.level1.KEY4 == new_key_value
        assert _settings.level1.key4 == new_key_value
        with pytest.raises(AttributeError):
            _settings.level1.key6
            _settings.level1.key7
            _settings.level1.KEY8
