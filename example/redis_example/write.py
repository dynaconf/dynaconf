from __future__ import annotations

from dynaconf import settings
from dynaconf.loaders import redis_loader

redis_loader.write(settings, {"SECRET": "redis_works"})

with settings.using_env("dev"):
    redis_loader.write(settings, {"SECRET": "redis_works_in_dev"})
