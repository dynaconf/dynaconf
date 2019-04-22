from dynaconf import settings

print(settings.YAML)
print(settings.HOST)
print(settings.PORT)


# using production values for context
with settings.using_env("PRODUCTION"):
    print(settings.ENVIRONMENT)
    print(settings.HOST)

# back to development env
print(settings.get("ENVIRONMENT"))
print(settings.HOST)
print(settings.WORKS)
