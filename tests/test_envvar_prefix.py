import os

from dynaconf import LazySettings

TOML = """
[global]
var = "my value"
"""


def test_envvar_prefix_lazysettings(tmpdir):
    os.environ["DYNACONF_PREFIXED_VAR"] = "this is prefixed"
    tmpfile = tmpdir.mkdir("sub").join("test_no_envvar_prefix.toml")
    tmpfile.write(TOML)

    settings = LazySettings(
        ENVVAR_PREFIX_FOR_DYNACONF=False, SETTINGS_FILE_FOR_DYNACONF=str(tmpfile)
    )

    assert settings.VAR == "my value"
    assert settings.DYNACONF_PREFIXED_VAR == "this is prefixed"
