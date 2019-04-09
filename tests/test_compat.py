from dynaconf import LazySettings


def test_compatibility_checks(tmpdir):
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
