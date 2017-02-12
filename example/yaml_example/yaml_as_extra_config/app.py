from dynaconf import settings

print(settings.YAML)
print(settings.HOST)
print(settings.PORT)


# using development: namespace values for context
with settings.using_namespace('DEVELOPMENT'):
    print(settings.ENVIRONMENT)
    print(settings.HOST)

# back to default dynaconf: namespace
print(settings.get('ENVIRONMENT'))
print(settings.HOST)