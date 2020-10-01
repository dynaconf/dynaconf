from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["configs/settings.toml", "configs/.secrets.toml"],
    environments=True,
)
