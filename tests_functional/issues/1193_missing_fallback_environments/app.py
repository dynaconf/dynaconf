from pathlib import Path

from dynaconf import Dynaconf

options = {
    "settings_files": [str(Path(__file__).with_name("settings.toml"))],
    "environments": True,
    "env": "development",
    "envvar_prefix": "APP",
    "silent_errors": False,
}

settings = Dynaconf(**options)
assert settings.value == "loaded"

try:
    settings.load_file(options["settings_files"], env="missing", silent=False)
except KeyError as exc:
    assert exc.args == ("missing",)
else:
    raise AssertionError("An explicitly requested environment must exist")

settings = Dynaconf(**options, loaders=["failing_loader"])
try:
    settings.as_dict()
except RuntimeError as exc:
    assert str(exc) == "Remote settings are unavailable"
else:
    raise AssertionError("The remote loader error must propagate")

options["silent_errors"] = True
settings = Dynaconf(**options, loaders=["failing_loader"])
assert settings.value == "loaded"
