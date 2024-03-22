from __future__ import annotations

import os
from pathlib import Path

from dynaconf import Dynaconf

env = {key: val for key, val in os.environ.items() if "DYNACONF" in key}
assert env == {}, f"Dynaconf environment not empty {env}"

os.environ["LOAD_DOTENV_FOR_DYNACONF"] = "true"

settings_files = [
    Path.cwd() / "config" / "settings.yaml",
    Path.cwd() / "config" / "settings-staging.yaml",
]

assert all(
    p.exists() for p in settings_files
), "Some of the given config files do not exist"

settings = Dynaconf(
    settings_files=settings_files,
    # load_dotenv=True
)

assert settings.FOO.get("bar") == "baz", (
    "Missing key FOO=bar in settings" + str(settings.FOO)
)
