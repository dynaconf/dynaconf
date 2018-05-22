from dynaconf import settings

# export DYNACONF_SETTINGS=settings.yaml
# or run $ source env.sh

# print all values in dynaconf: env of yaml file
print(settings.HOST)
print(settings.PORT)
print(settings.USERNAME)
print(settings.PASSWORD)
print(settings.LEVELS)
print(settings.TEST_LOADERS)
print(settings.MONEY)
print(settings.AGE)
print(settings.ENABLED)

# using development: env values for context
with settings.using_env('DEVELOPMENT'):
    print(settings.ENVIRONMENT)
    print(settings.HOST)

# back to default dynaconf: env
print(settings.get('ENVIRONMENT'))
print(settings.HOST)

# set env to development:
settings.setenv('development')
print(settings.HOST)
print(settings.ENVIRONMENT)

# back to default env again
settings.setenv()
print(settings.HOST)
print(settings.get('ENVIRONMENT'))

print(settings.WORKS)
