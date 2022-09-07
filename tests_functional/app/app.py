from __future__ import annotations

from dynaconf import settings

print(settings.MYSQL_HOST)  # noqa
print(settings.MYSQL_PASSWD)  # noqa
print(settings.EXAMPLE)  # noqa
print(settings.WORKS)  # noqa


assertions = {
    "EXAMPLE": True,
    "MYSQL_HOST": "server.com",
    "WORKS": "app",
    "MYSQL_PASSWD": "SuperSecret",
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
