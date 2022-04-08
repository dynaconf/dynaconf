from dynaconf import Dynaconf


# No prefix.
settings = Dynaconf(
    settings_file="settings.toml",
    load_dotenv=True,
    ignore_unknown_envvars=True,
    envvar_prefix=False,
)

assert settings.VAR1 == "bar"
assert not settings.get("SECRET")


# MYAPP_ prefix.
settings = Dynaconf(
    settings_file="settings.toml",
    load_dotenv=True,
    ignore_unknown_envvars=True,
    envvar_prefix="MYAPP",
)

assert settings.VAR1 == "ham"
assert not settings.get("SECRET")
