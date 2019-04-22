from dynaconf import settings

# print all values in the file
# using [default] + [development] + [global] values
print("* All values")
print(settings.HOST)
print(settings.PORT)
print(settings.USERNAME)
print(settings.PASSWORD)
print(settings.LEVELS)
print(settings.TEST_LOADERS)
print(settings.MONEY)
print(settings.AGE)
print(settings.ENABLED)
print(settings.CUSTOM)

print("* Switiching to production")
# using [production] env values for context
with settings.using_env("PRODUCTION"):
    print(settings.CUSTOM)
    print(settings.HOST)

print("* Switiching to development")
# back to default [development] env
print(settings.get("CUSTOM"))
print(settings.HOST)

print("* Switiching to production")
# set env to [production]:
settings.setenv("production")
print(settings.HOST)
print(settings.CUSTOM)

print("* Switiching to development")
# back to [development] env again
settings.setenv()
print(settings.HOST)
print(settings.get("INEXISTENT"))  # None

print(settings.WORKS)
