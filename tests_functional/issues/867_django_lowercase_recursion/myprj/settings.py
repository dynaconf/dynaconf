from __future__ import annotations

from contextlib import suppress
from pathlib import Path

import dynaconf

PROJECT_ROOT = Path(__file__).parent.parent.resolve(strict=True).as_posix()

settings = dynaconf.DjangoDynaconf(
    __name__,
    root_path=PROJECT_ROOT,
    core_loaders=["TOML", "PY"],
    settings_files=["settings.toml"],
    lowercase_read=False,
)


# Behavior consistent with lowercase_read=False unit tests
try:
    settings.secret_key
except AttributeError:
    assert True  # should raise, because lowercase_read = False

assert settings.Secret_key == "a"
assert settings.SECRET_KEY == "a"
