from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_files="settings.yaml", environments=True)


print(settings.get("level1").get("level2").get("level3"))
print(settings.get("level1").get("level2"))
print(settings.get("level1"))


print(settings.get("level1.level2.level3"))
print(settings.get("level1.level2"))
print(settings.get("level1"))


print(settings.get("template"))
print(settings.get("value0"))
print(settings.get("level1.value1"))
print(settings.get("level1.level2.value2"))
print(settings.get("level1.level2.level3.value3"))


assert settings.get("level1.level2.level3").to_dict() == {
    "value3": "Whoohoo world/level3/jinja"
}
assert settings.get("level1.level2").to_dict() == {
    "value2": "HELLO world/level2/jinja",
    "level3": {"value3": "Whoohoo world/level3/jinja"},
}
assert settings.get("level1").to_dict() == {
    "template2": "Whoohoo @tpl@",
    "value1": "HELLO @tpl@/level1/format",
    "level2": {
        "value2": "HELLO world/level2/jinja",
        "level3": {"value3": "Whoohoo world/level3/jinja"},
    },
}

assert settings.get("template") == "HELLO @tpl@"
assert settings.get("value0") == "HELLO world/level0/jinja"
assert settings.get("level1.value1") == "HELLO @tpl@/level1/format"
assert settings.get("level1.level2.value2") == "HELLO world/level2/jinja"
assert (
    settings.get("level1.level2.level3.value3") == "Whoohoo world/level3/jinja"
)
