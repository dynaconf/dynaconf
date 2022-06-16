from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
)

assert settings.key == "value"
assert settings.number == 789
assert settings.a_dict.nested.other_level == "nested value"
assert settings["a_boolean"] is False
assert settings.get("DONTEXIST", default=1) == 1


for item in settings:
    print(item)


for key, value in settings.items():  # dict like iteration
    print(key, value)
