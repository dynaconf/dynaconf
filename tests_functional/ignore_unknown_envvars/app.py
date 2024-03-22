from __future__ import annotations

from dynaconf import LazySettings

# No prefix.
settings = LazySettings(
    settings_file="settings.toml",
    load_dotenv=True,
    ignore_unknown_envvars=True,
    envvar_prefix=False,
)

assert settings.VAR1 == "bar"
assert not settings.get("SECRET")


# MYAPP_ prefix.
settings = LazySettings(
    settings_file="settings.toml",
    load_dotenv=True,
    ignore_unknown_envvars=True,
    envvar_prefix="MYAPP",
)

assert settings.VAR1 == "ham"
assert not settings.get("SECRET")
