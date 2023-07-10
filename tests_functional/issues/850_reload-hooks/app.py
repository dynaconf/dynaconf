"""
Assert settings.reload() re-reruns hooks.
"""
from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.toml")

assert settings.counter == 1
settings.reload()
assert settings.counter == 1
