from __future__ import annotations

import os

import pytest

from dynaconf import LazySettings


@pytest.mark.parametrize(
    "deprecated,value,new",
    [
        ("DYNACONF_NAMESPACE", "FOO", "ENV_FOR_DYNACONF"),
        ("NAMESPACE_FOR_DYNACONF", "FOO", "ENV_FOR_DYNACONF"),
        ("DYNACONF_SETTINGS_MODULE", "dfoo.py", "SETTINGS_FILE_FOR_DYNACONF"),
        ("SETTINGS_MODULE", "dfoo.py", "SETTINGS_FILE_FOR_DYNACONF"),
        ("PROJECT_ROOT", "./", "ROOT_PATH_FOR_DYNACONF"),
        ("DYNACONF_SILENT_ERRORS", True, "SILENT_ERRORS_FOR_DYNACONF"),
        ("DYNACONF_ALWAYS_FRESH_VARS", ["BAR"], "FRESH_VARS_FOR_DYNACONF"),
        ("GLOBAL_ENV_FOR_DYNACONF", "MYAPP", "ENVVAR_PREFIX_FOR_DYNACONF"),
        ("BASE_NAMESPACE_FOR_DYNACONF", "THIS", "DEFAULT_ENV_FOR_DYNACONF"),
    ],
)
def test_dynaconf_namespace_renamed(tmpdir, recwarn, deprecated, value, new):
    settings = LazySettings(**{deprecated: value})

    assert len(recwarn) == 1
    assert issubclass(recwarn[0].category, DeprecationWarning)
    assert deprecated in str(recwarn[0].message)
    assert new in str(recwarn[0].message)
    assert settings.get(new) == value


def test_envvar_prefix_for_dynaconf(tmpdir, recwarn):
    os.environ["AWESOMEAPP_FOO"] = "1"
    os.environ["AWESOMEAPP_BAR"] = "false"
    os.environ["AWESOMEAPP_LIST"] = '["item1", "item2"]'
    os.environ["AWESOMEAPP_FLOAT"] = "42.2"

    settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF="AWESOMEAPP")

    assert settings.FOO == 1
    assert settings.BAR is False
    assert settings.LIST == ["item1", "item2"]
    assert settings.FLOAT == 42.2

    settings2 = LazySettings(GLOBAL_ENV_FOR_DYNACONF="AWESOMEAPP")

    assert len(recwarn) == 1
    assert issubclass(recwarn[0].category, DeprecationWarning)
    assert "GLOBAL_ENV_FOR_DYNACONF" in str(recwarn[0].message)

    assert settings2.FOO == 1
    assert settings2.BAR is False
    assert settings2.LIST == ["item1", "item2"]
    assert settings2.FLOAT == 42.2
