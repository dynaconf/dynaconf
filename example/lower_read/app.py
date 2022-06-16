from __future__ import annotations

from dynaconf import LazySettings

settings = LazySettings(settings_files="settings.yaml")

assert settings.server == "foo.com"
assert settings.SERVER == "foo.com"
assert settings["SERVER"] == "foo.com"
assert settings["server"] == "foo.com"
assert settings("SERVER") == "foo.com"
assert settings("server") == "foo.com"
assert settings.get("SERVER") == "foo.com"
assert settings.get("server") == "foo.com"
