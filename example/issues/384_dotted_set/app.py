from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf()

settings.set("a.b", 1)
settings.set("a.c", 2)
settings.set("a.c.k", 22)

assert settings.a == {"c": {"k": 22}, "b": 1}

settings.set("a.c.b", 3)

assert settings.a == {"c": {"b": 3, "k": 22}, "b": 1}
