from dynaconf import Dynaconf

settings = Dynaconf(**options)
from dynaconf.loaders import redis_loader

redis_loader.write(settings, {"SECRET": "redis_works"})

with settings.using_env("dev"):
    redis_loader.write(settings, {"SECRET": "redis_works_in_dev"})
