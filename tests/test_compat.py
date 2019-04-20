import os
from dynaconf import LazySettings


def test_dynaconf_namespace_renamed(tmpdir):
    settings = LazySettings(
        DYNACONF_NAMESPACE='FOO',
        DYNACONF_SETTINGS_MODULE='foo.py',
        SETTINGS_MODULE='foo.py',
        PROJECT_ROOT=str(tmpdir),
        DYNACONF_SILENT_ERRORS=True,
        DYNACONF_ALWAYS_FRESH_VARS=['BAR']
    )

    assert settings.ENV_FOR_DYNACONF == 'FOO'
    assert settings.SETTINGS_MODULE_FOR_DYNACONF == 'foo.py'
    assert settings.ROOT_PATH_FOR_DYNACONF == str(tmpdir)
    assert settings.SILENT_ERRORS_FOR_DYNACONF is True
    assert settings.FRESH_VARS_FOR_DYNACONF == ['BAR']


def test_namespace_for_dynaconf_renamed(tmpdir):
    settings = LazySettings(
        NAMESPACE_FOR_DYNACONF='FOO',
        DYNACONF_SETTINGS_MODULE='foo.py',
        SETTINGS_MODULE='foo.py',
        PROJECT_ROOT_FOR_DYNACONF=str(tmpdir),
        DYNACONF_SILENT_ERRORS=True,
        DYNACONF_ALWAYS_FRESH_VARS=['BAR']
    )

    assert settings.ENV_FOR_DYNACONF == 'FOO'
    assert settings.SETTINGS_MODULE_FOR_DYNACONF == 'foo.py'
    assert settings.ROOT_PATH_FOR_DYNACONF == str(tmpdir)
    assert settings.SILENT_ERRORS_FOR_DYNACONF is True
    assert settings.FRESH_VARS_FOR_DYNACONF == ['BAR']


def test_envvar_prefix_for_dynaconf(tmpdir):
    os.environ['AWESOMEAPP_FOO'] = '1'
    os.environ['AWESOMEAPP_BAR'] = 'false'
    os.environ['AWESOMEAPP_LIST'] = '["item1", "item2"]'
    os.environ['AWESOMEAPP_FLOAT'] = '42.2'

    settings = LazySettings(
        ENVVAR_PREFIX_FOR_DYNACONF='AWESOMEAPP'
    )

    assert settings.FOO == 1
    assert settings.BAR is False
    assert settings.LIST == ["item1", "item2"]
    assert settings.FLOAT == 42.2

    settings2 = LazySettings(
        GLOBAL_ENV_FOR_DYNACONF='AWESOMEAPP'
    )

    assert settings2.FOO == 1
    assert settings2.BAR is False
    assert settings2.LIST == ["item1", "item2"]
    assert settings2.FLOAT == 42.2
