from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="INSPECT",
    settings_file="settings.yaml",
    load_dotenv=True,
)
settings.load_file("thefile.py")
settings.load_file("thefile.toml")
