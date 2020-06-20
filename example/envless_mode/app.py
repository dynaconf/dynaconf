import os

from dynaconf import LazySettings

settings = LazySettings()


assert settings.FOO == "bar"
assert settings.HELLO == "world"
assert settings.DATABASES.default.port == 8080
assert settings.LAZY == os.environ["HOME"]
