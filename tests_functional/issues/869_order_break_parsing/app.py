from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.yaml",
    load_dotenv=True,
)

# issue example
assert settings.as_dict()
assert settings.ROOT == str(Path().absolute().parent)

# possible merging side-effects related to workaround
assert settings.MERGING[0] == settings.SUBDIR
assert settings.MERGING[1] == settings.ROOT_REL
