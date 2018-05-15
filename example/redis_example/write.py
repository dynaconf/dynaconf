from dynaconf import settings
from dynaconf.loaders import redis_loader

redis_loader.write(settings, {'SECRET': 'redis_works'})

with settings.using_namespace('dev'):
    redis_loader.write(settings, {'SECRET': 'redis_works_in_dev'})
