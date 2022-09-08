from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", "settings.yaml"],
    environments=True,
    load_dotenv=True,
)

assert settings.SOME_DICT.value == "formatted: foo", settings.SOME_DICT.value

assert settings.INNER1.value == "inner1 str foo"
assert settings.INNER1.VALUE_LIST[0] == "list 0 foo"
assert settings.INNER1.INNER2.value == "inner2 str inner1 str foo"

assert settings.TOP_LEVEL_LIST[0] == "top list foo"
assert settings.TOP_LEVEL_LIST[3] == "a jinja formatted FOO"

assert settings.get("TOP_LEVEL_LIST")[0] == "top list foo"
assert settings.get("TOP_LEVEL_LIST")[3] == "a jinja formatted FOO"

settings.set("INITIAL", "@merge [9, 8, 7]")


settings.set("DATABASES.default.PARAMS", '@merge_unique ["e", "f", "g"]')

assert settings.DATABASES == {"default": {"PARAMS": ["d", "e", "f", "g"]}}
assert settings.INITIAL == [3, 2, 2, 1, 1, 1, 2, 3, 9, 8, 7], settings.INITIAL
