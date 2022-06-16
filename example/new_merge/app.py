from __future__ import annotations

from dynaconf import settings

assert settings.PY_MERGE_LIST == [1, 2], settings.PY_MERGE_LIST
assert settings.PY_MERGE_DICT == {"a": 1, "b": 2}, settings.PY_MERGE_DICT

for filename in [
    "settings.py",
    "settings.local.py",
    "settings.toml",
    "settings.local.toml",
    "settings.yaml",
    "settings.local.yaml",
    ".env",
]:
    assert filename in settings.FILES, settings.FILES


assert settings.PERSON.name == "Bruno", settings.PERSON
assert settings.PERSON.age == 36, settings.PERSON
assert settings.PERSON.city == "Guarulhos", settings.PERSON
assert settings.PERSON.country == "Brasil", settings.PERSON
assert settings.PERSON.email == "bruno@example.com", settings.PERSON
assert settings.PERSON.phone == "123-456", settings.PERSON

print(settings.FILES)
print(settings.PERSON)
