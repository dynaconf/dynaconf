from dynaconf import settings

print(settings.YAML)
print(settings.HOST)
print(settings.PORT)


# using development: env values for context
with settings.using_env('DEVELOPMENT'):
    print(settings.ENVIRONMENT)
    print(settings.HOST)

# back to default dynaconf: env
print(settings.get('ENVIRONMENT'))
print(settings.HOST)
print(settings.WORKS)
