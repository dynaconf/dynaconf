from __future__ import annotations

from conf import settings

print(settings.MYSQL_HOST)  # noqa
print(settings.MYSQL_PASSWD)  # noqa
print(settings.EXAMPLE)  # noqa

print(settings.current_env)  # noqa
print(settings.WORKS)  # noqa


assertions = {
    "AGE": 15,
    "A_DICT": {"NESTED_1": {"NESTED_2": {"NESTED_3": {"NESTED_4": 1}}}},
    "BASE_IMAGE": "bla",
    "DEV_SERVERS": ["127.0.0.1", "localhost", "development.com"],
    "EXAMPLE": True,
    "MYSQL_HOST": "localhost",
    "NAME": "BRUNO",
    "PORT": 8001,
    "PRESIDENT": "Lula",
    "PROJECT": "hello_world",
    "SALARY": 2000,
    "VERSION": 1,
    "WORKS": "validator",
    "MYSQL_PASSWD": "SuperSecret",
    "FOOBAR": "EMPTY",
}


for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


assertions = {
    "AGE": 15,
    "A_DICT": {"NESTED_1": {"NESTED_2": {"NESTED_3": {"NESTED_4": 1}}}},
    "BASE_IMAGE": "bla",
    "DEV_SERVERS": ["127.0.0.1", "localhost", "development.com"],
    "EXAMPLE": True,
    "MYSQL_HOST": "development.com",
    "NAME": "MIKE",
    "PORT": 8001,
    "PRESIDENT": "Lula",
    "PROJECT": "hello_world",
    "SALARY": 2000,
    "VERSION": 1,
    "WORKS": "validator",
    "IMAGE_1": "aaa",
    "IMAGE_2": "bbb",
    "IMAGE_4": "a",
    "IMAGE_5": "b",
    "MYSQL_PASSWD": "SuperSecret",
}


for key, value in assertions.items():
    found = settings.from_env("development").get(key)
    assert found == getattr(settings.from_env("development"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"


assertions = {
    "AGE": 15,
    "A_DICT": {"NESTED_1": {"NESTED_2": {"NESTED_3": {"NESTED_4": 1}}}},
    "BASE_IMAGE": "bla",
    "DEV_SERVERS": ["127.0.0.1", "localhost", "development.com"],
    "EXAMPLE": True,
    "MYSQL_HOST": "production.com",
    "NAME": "MIKE",
    "PORT": 8001,
    "PRESIDENT": "Lula",
    "PROJECT": "hello_world",
    "SALARY": 2000,
    "VERSION": 1,
    "WORKS": "validator",
    "IMAGE_4": "a",
    "IMAGE_5": "b",
    "MYSQL_PASSWD": "SuperSecret",
}

for key, value in assertions.items():
    found = settings.from_env("production").get(key)
    assert found == getattr(settings.from_env("production"), key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
