from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    root_path=Path(__file__).parent,
    envvar_prefix="PP",
    settings_files=["defaults.toml", "../etc/settings.toml"],
    pyproject_section="pp_settings",
    load_dotenv=True,
    loaders=["src.pyproject_loader", "dynaconf.loaders.env_loader"],
)

assert settings.debug is True
assert settings.foo == "bar"
assert settings.xpto == "abcd"
assert settings.colors == ["red", "green", "blue", "white", "black"]
assert settings.person == {
    "work": {"lang": "Python", "company": "PSF"},
    "country": "Netherlands",
    "lastname": "Rossum",
    "name": "Guido",
}
