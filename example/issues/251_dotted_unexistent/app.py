from __future__ import annotations

from dynaconf import settings

print("As dict:")
print(settings.as_dict())

assert settings.FOO == {"bar": "hello"}
assert settings.FOO.bar == "hello"

assert settings.get("FOO") == {"bar": "hello"}
assert settings.get("foo") == {"bar": "hello"}
assert settings.get("foo.bar") == "hello", settings.get("foo.bar")

assert settings.get("foo.zaz") is None
assert settings.get("non.zaz") is None
assert settings.get("non.zaz", 3) == 3
print("With list as default 1:")
assert settings.get("non.existing.key", [1, 2, 3]) == [1, 2, 3]
assert settings.get("non.zaz", 3) == 3

assert settings.get("foo.bar") == "hello"

print("With 0 as default:")
assert settings.get("non.existing.key", 0) == 0

print("With list as default 2:")
assert settings.get("non.existing.key", [4, 5, 6]) == [4, 5, 6]
