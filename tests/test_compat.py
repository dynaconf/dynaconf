from dynaconf import LazySettings


def test_compatibility_checks():
    settings = LazySettings(
        DYNACONF_NAMESPACE='FOO',
        DYNACONF_SETTINGS_MODULE='foo.py',
        SETTINGS_MODULE='foo.py',
        PROJECT_ROOT='/tmp',
        DYNACONF_SILENT_ERRORS=True,
        DYNACONF_ALWAYS_FRESH_VARS=['BAR']
    )

    assert settings.NAMESPACE_FOR_DYNACONF == 'FOO'
    assert settings.SETTINGS_MODULE_FOR_DYNACONF == 'foo.py'
    assert settings.PROJECT_ROOT_FOR_DYNACONF == '/tmp'
    assert settings.SILENT_ERRORS_FOR_DYNACONF is True
    assert settings.FRESH_VARS_FOR_DYNACONF == ['BAR']
