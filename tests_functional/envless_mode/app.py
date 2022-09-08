from __future__ import annotations

import os

from dynaconf import LazySettings

settings = LazySettings(settings_file="settings.yaml")


assert settings.FOO == "bar"
assert settings.HELLO == "world"
assert settings.DATABASES.default.port == 8080
assert settings.LAZY == os.environ["HOME"]
