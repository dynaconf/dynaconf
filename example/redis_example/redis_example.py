from dynaconf import settings

print(settings.SECRET)  # noqa
# >>> 'redis_works'


with settings.using_namespace('dev'):
    assert settings.SECRET == 'redis_works_in_dev'
