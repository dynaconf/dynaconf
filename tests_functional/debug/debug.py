from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(settings_file="settings.toml")


__import__("pudb").set_trace()

foo = settings.store.get("foo")
bar = foo.bar
