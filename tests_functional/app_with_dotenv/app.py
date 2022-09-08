from __future__ import annotations

from dynaconf import settings

print(settings.MYSQL_HOST)  # noqa
print(settings.MYSQL_PASSWD)  # noqa
print(settings.EXAMPLE)  # noqa  # noqa
print(settings.MYSQL_HOST)  # noqa
print(settings.MYSQL_PASSWD)  # noqa
print(settings.EXAMPLE)  # noqa
print(settings.MONEY_VALUE)  # noqa
print(settings.BOOL_VALUE)  # noqa
print(settings.JSON_VALUE)  # noqa
print(settings.WORKS)  # noqa


assertions = {
    "EXAMPLE": "Hello World",
    "MYSQL_HOST": "server.com",
    "WORKS": "app_with_dotenv",
    "MYSQL_PASSWD": 123456,
    "MONEY_VALUE": 345.6,
    "BOOL_VALUE": False,
    "JSON_VALUE": ["a", "b"],
    "SETTINGS_FILE_FOR_DYNACONF": "/tmp/bla.py",
    "TOML_LIST": [1, 2, 3],
    "TOML_DICT": {"a": 1, "b": 2},
    "COLORS": {"white": {"code": "#FFFFFF", "name": "White"}},
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
