from __future__ import annotations

import os

from dynaconf import Dynaconf

settings = Dynaconf(
    environments=True,
    lowercase_read=False,
    load_dotenv=True,
    root_path=os.path.dirname(os.path.abspath(__file__)),
    settings_files=["settings.toml", ".config/*.yaml"],
)

assert settings.LOG_LEVEL == "INFO"
assert settings.DATA_SOURCES == {"NAME": 1}
print(settings.LOG_LEVEL)
print(settings.DATA_SOURCES)
