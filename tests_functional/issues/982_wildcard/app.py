from __future__ import annotations

import os
import sys

# If python version is <  3.10 skip test
# glob on that version of Python doesnt have root_dir param
if sys.version_info < (3, 10):
    print("Skip test")
    sys.exit(0)

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
