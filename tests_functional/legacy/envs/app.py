from __future__ import annotations

from dynaconf import settings

print(
    f"# 1 all values in {settings.DEFAULT_ENV_FOR_DYNACONF}"
    f"{settings.current_env}: env of yaml file:"
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
    print(f"# 2 using {settings.current_env}: env values for context:")
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

print(f"# 3 back to default {settings.current_env}: env:")
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
print(f"# 4 Set to {settings.current_env}: env:")
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
print(f"# 5 back to default {settings.current_env}: env:")
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
    print(f"# 6 using {settings.current_env}: env values for context:")
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

print(f"# 7 back to default {settings.current_env}: env:")
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
print(f"# 8 Set to {settings.current_env}: env:")
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
print(f"# 9 back to default {settings.current_env}: env:")
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
