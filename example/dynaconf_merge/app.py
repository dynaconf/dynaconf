from dynaconf import Dynaconf

settings = Dynaconf(**options)

assert settings.DATABASE == {
    "host": "dev.server.com",
    "user": "dev",
    "port": 666,
    "passwd": "1234",
}, settings.DATABASE


assert settings.PLUGINS == [
    "core",
    "debug_toolbar",
    "secret",
], settings.PLUGINS
