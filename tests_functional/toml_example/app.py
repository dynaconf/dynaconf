from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import settings
from dynaconf.strategies.filtering import PrefixFilter

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

print("* Switching to production")
# using [production] env values for context
with settings.using_env("PRODUCTION"):
    print(settings.CUSTOM)
    print(settings.HOST)

print("* Switching to development")
# back to default [development] env
print(settings.get("CUSTOM"))
print(settings.HOST)

print("* Switching to production")
# set env to [production]:
settings.setenv("production")
print(settings.HOST)
print(settings.CUSTOM)

print("* Switching to development")
# back to [development] env again
settings.setenv()
print(settings.HOST)
print(settings.get("INEXISTENT"))  # None

print(settings.WORKS)


assertions = {
    "HOST": "dev_server.com from toml",
    "PORT": 5000,
    "USERNAME": "admin",
    "PASSWORD": "Secret",
    "LEVELS": ["debug", "info", "warning"],
    "MONEY": 500.5,
    "AGE": 42,
    "ENABLED": True,
    "WORKS": "toml_example in dev env",
    "CUSTOM": "this is custom from [development]",
    "PREFIX_CUSTOM": "this is custom when we set a prefix",
    "TEST_LOADERS": {"dev": "test_dev", "prod": "test_prod"},
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


assertions = {
    "HOST": "prod_server.com from toml",
    "PORT": 5000,
    "USERNAME": "admin",
    "PASSWORD": "Secret",
    "LEVELS": ["debug", "info", "warning"],
    "MONEY": 500.5,
    "AGE": 42,
    "ENABLED": True,
    "WORKS": "toml_example in prod env",
    "CUSTOM": "this is custom from [production]",
    "TEST_LOADERS": {"dev": "test_dev", "prod": "test_prod"},
}


for key, value in assertions.items():
    found = settings.from_env("production").get(key)
    assert found == getattr(settings.from_env("production"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


settings_with_prefix = Dynaconf(
    settings_files=["settings.toml"],
    filter_strategy=PrefixFilter("prefix"),
    environments=True,
)
with settings_with_prefix.using_env("default"):
    assert settings_with_prefix.CUSTOM == "this is custom when we set a prefix"
assert (
    settings_with_prefix.from_env("production").CUSTOM
    == "this is custom when we set a prefix"
)
