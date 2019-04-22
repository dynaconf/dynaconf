from dynaconf import settings


print(
    "# 1 all values in {} + {}: env of yaml file:".format(
        settings.DEFAULT_ENV_FOR_DYNACONF, settings.current_env
    )
)
assert settings.current_env == "DEVELOPMENT"
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)

with settings.using_env("TESTING"):
    print("# 2 using {}: env values for context:".format(settings.current_env))
    assert settings.current_env == "TESTING"
    print("HOST::", settings.HOST)
    print("PORT:", settings.PORT)
    print("USERNAME:", settings.USERNAME)
    print("PASSWORD:", settings.PASSWORD)
    print("LEVELS:", settings.LEVELS)
    print("TEST_LOADERS:", settings.TEST_LOADERS)
    print("MONEY:", settings.MONEY)
    print("AGE:", settings.AGE)
    print("ENABLED:", settings.ENABLED)
    print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
    print("WORKS:", settings.WORKS)

print("# 3 back to default {}: env:".format(settings.current_env))
assert settings.current_env == "DEVELOPMENT"
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)

settings.setenv("testing")
print("# 4 Set to {}: env:".format(settings.current_env))
assert settings.current_env == "TESTING"
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)

settings.setenv()
print("# 5 back to default {}: env:".format(settings.current_env))
assert settings.current_env == "DEVELOPMENT"
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)


with settings.using_env("staging"):
    print("# 6 using {}: env values for context:".format(settings.current_env))
    assert settings.current_env == "STAGING"
    print("HOST::", settings.HOST)
    print("PORT:", settings.PORT)
    print("USERNAME:", settings.USERNAME)
    print("PASSWORD:", settings.PASSWORD)
    print("LEVELS:", settings.LEVELS)
    print("TEST_LOADERS:", settings.TEST_LOADERS)
    print("MONEY:", settings.MONEY)
    print("AGE:", settings.AGE)
    print("ENABLED:", settings.ENABLED)
    print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
    print("WORKS:", settings.WORKS)

print("# 7 back to default {}: env:".format(settings.current_env))
assert settings.current_env == "DEVELOPMENT"
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)

settings.setenv("staging")
assert settings.current_env == "STAGING"
print("# 8 Set to {}: env:".format(settings.current_env))
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)

settings.setenv()
print("# 9 back to default {}: env:".format(settings.current_env))
print("HOST::", settings.HOST)
print("PORT:", settings.PORT)
print("USERNAME:", settings.USERNAME)
print("PASSWORD:", settings.PASSWORD)
print("LEVELS:", settings.LEVELS)
print("TEST_LOADERS:", settings.TEST_LOADERS)
print("MONEY:", settings.MONEY)
print("AGE:", settings.AGE)
print("ENABLED:", settings.ENABLED)
print("ENVIRONMENT:", settings.get("ENVIRONMENT"))
print("WORKS:", settings.WORKS)


assert settings.current_env == "DEVELOPMENT"
