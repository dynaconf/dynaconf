from __future__ import annotations

from dynaconf import LazySettings

settings = LazySettings(
    environments=True,
    ENV_FOR_DYNACONF="example",
    ENVVAR_PREFIX_FOR_DYNACONF="PROGRAM",
    load_dotenv=True,
    settings_files="settings.toml;.secrets.toml",
)

print(settings.USERNAME)
print(settings.SERVER)
print(settings.PASSWORD)


assertions = {
    "SERVER": "fromenv.com",
    "USERNAME": "admin",
    "PASSWORD": "My5up3r53c4et",
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


assertions = {"SERVER": "fromenv.com", "USERNAME": "foo"}

for key, value in assertions.items():
    found = settings.from_env("development").get(key)
    assert found == getattr(settings.from_env("development"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"

assertions = {
    "SERVER": "fromenv.com",
    "USERNAME": "foo",
    "PASSWORD": "My5up3r53c4et",  # keep=True will keep it from [example] env
}

for key, value in assertions.items():
    found = settings.from_env("development", keep=True).get(key)
    assert found == getattr(settings.from_env("development", keep=True), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
