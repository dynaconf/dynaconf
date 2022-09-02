from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from dynaconf.utils import parse_conf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml"],
    environments=True,
)

# Add a custom casting token casting string to pathlib.Path object
parse_conf.converters["@path"] = (
    lambda value: value.set_casting(Path)
    if isinstance(value, parse_conf.Lazy)
    else Path(value)
)

assert isinstance(settings.parent, Path)
assert isinstance(settings.child, Path)
assert str(settings.child).find("@format") == -1
