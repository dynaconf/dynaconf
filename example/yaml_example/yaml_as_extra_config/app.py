from __future__ import annotations

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


assertions = {
    "HOST": "dev_server.com",
    "PORT": 5000,
    "ENVIRONMENT": "this is development",
    "WORKS": "yaml_as_extra_config",
}


for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


assertions = {
    "HOST": "prod_server.com",
    "PORT": 5000,
    "ENVIRONMENT": "this is production",
}


for key, value in assertions.items():
    found = settings.from_env("production").get(key)
    assert found == getattr(settings.from_env("production"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
