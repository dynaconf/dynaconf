from dynaconf import settings

# export DYNACONF_SETTINGS=settings.yaml
# or run $ source env.sh

# print all values in dynaconf: namespace of yaml file
print(settings.HOST)
print(settings.PORT)
print(settings.USERNAME)
print(settings.PASSWORD)
print(settings.LEVELS)
print(settings.TEST_LOADERS)
print(settings.MONEY)
print(settings.AGE)
print(settings.ENABLED)

# using development: namespace values for context
with settings.using_namespace('DEVELOPMENT'):
    print(settings.ENVIRONMENT)
    print(settings.HOST)

# back to default dynaconf: namespace
print(settings.get('ENVIRONMENT'))
print(settings.HOST)

# set namespace to development:
settings.namespace('development')
print(settings.HOST)
print(settings.ENVIRONMENT)

# back to default namespace again
settings.namespace()
print(settings.HOST)
print(settings.get('ENVIRONMENT'))

print(settings.WORKS)
