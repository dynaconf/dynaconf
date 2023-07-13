from __future__ import annotations

import os

from dynaconf import Dynaconf

print(os.getenv("SETTINGS_FILE_FOR_DYNACONF"))
settings = Dynaconf()

print(settings.offset)
assert settings.offset == 24

settings.validators.validate()

print(type(settings.offset))
assert isinstance(settings.offset, int)
