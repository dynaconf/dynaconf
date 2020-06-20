from dynaconf import LazySettings
from dynaconf.utils import RENAMED_VARS


# 0 given a bare settings
settings = LazySettings(environments=True)

# 1 Ensure all renamed vars exists in object
for old, new in RENAMED_VARS.items():
    assert old in settings
    assert new in settings

# 2 Ensure pairs has the same value
for old, new in RENAMED_VARS.items():
    assert settings.get(old) == settings.get(new)
    assert getattr(settings, new) == getattr(settings, old)


# 0 given a full old-style configured setting
settings = LazySettings(
    environments=True,
    DYNACONF_NAMESPACE="FOO",
    DYNACONF_SETTINGS_MODULE="/tmp/foo.toml",
    PROJECT_ROOT="/tmp/",
    DYNACONF_SILENT_ERRORS=False,
    DYNACONF_ALWAYS_FRESH_VARS=["baz", "zaz", "caz"],
    BASE_NAMESPACE_FOR_DYNACONF="original",
    GLOBAL_ENV_FOR_DYNACONF="RAZAMANAZ",
)

# 1 Ensure all renamed vars exists in object
for old, new in RENAMED_VARS.items():
    assert old in settings, old
    assert new in settings, new

# 2 Ensure pairs has the same value
for old, new in RENAMED_VARS.items():
    assert settings.get(old) == settings.get(new), (
        old,
        settings.get(old),
        new,
        settings.get(new),
    )
    assert getattr(settings, new) == getattr(settings, old), (
        new,
        getattr(settings, new),
        old,
        getattr(settings, old),
    )

settings = LazySettings(
    environments=True,
    DYNACONF_NAMESPACE="FOO",
    DYNACONF_SETTINGS_MODULE="foo.py",
    PROJECT_ROOT="/tmp",
    DYNACONF_SILENT_ERRORS=True,
    DYNACONF_ALWAYS_FRESH_VARS=["BAR"],
    GLOBAL_ENV_FOR_DYNACONF="BLARG",
)


assert settings.ENV_FOR_DYNACONF == "FOO"
assert settings.SETTINGS_FILE_FOR_DYNACONF == "foo.py"
assert settings.ROOT_PATH_FOR_DYNACONF == "/tmp"
assert settings.SILENT_ERRORS_FOR_DYNACONF is True
assert settings.FRESH_VARS_FOR_DYNACONF == ["BAR"]
assert settings.ENVVAR_PREFIX_FOR_DYNACONF == "BLARG"

print(settings.ENV_FOR_DYNACONF)
print(settings.SETTINGS_FILE_FOR_DYNACONF)
print(settings.ROOT_PATH_FOR_DYNACONF)
print(settings.SILENT_ERRORS_FOR_DYNACONF)
print(settings.FRESH_VARS_FOR_DYNACONF)


settings = LazySettings(
    environments=True,
    NAMESPACE="FOO",
    SETTINGS_MODULE="foo.py",
    PROJECT_ROOT="/tmp",
    DYNACONF_SILENT_ERRORS=True,
    DYNACONF_ALWAYS_FRESH_VARS=["BAR"],
)


assert settings.ENV_FOR_DYNACONF == "FOO"
assert settings.SETTINGS_FILE_FOR_DYNACONF == "foo.py"
assert settings.ROOT_PATH_FOR_DYNACONF == "/tmp"
assert settings.SILENT_ERRORS_FOR_DYNACONF is True
assert settings.FRESH_VARS_FOR_DYNACONF == ["BAR"]

print(settings.ENV_FOR_DYNACONF)
print(settings.SETTINGS_FILE_FOR_DYNACONF)
print(settings.ROOT_PATH_FOR_DYNACONF)
print(settings.SILENT_ERRORS_FOR_DYNACONF)
print(settings.FRESH_VARS_FOR_DYNACONF)
