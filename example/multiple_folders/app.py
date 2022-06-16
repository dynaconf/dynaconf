from __future__ import annotations

from dynaconf import settings

print("development")
print(settings.VAR1)
print(settings.VAR2)


assertions = {"VAR1": "var1_dev", "VAR2": "var2_dev"}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


print("production")
print(settings.from_env("production").VAR1)
print(settings.from_env("production").VAR2)

assertions = {"VAR1": "var1_prod", "VAR2": "var2_prod"}

for key, value in assertions.items():
    found = settings.from_env("production").get(key)
    assert found == getattr(settings.from_env("production"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
