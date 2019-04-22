from dynaconf import settings

print(settings.SECRET)  # noqa
# >>> 'redis_works'


with settings.using_env("dev"):
    assert settings.SECRET == "redis_works_in_dev"
