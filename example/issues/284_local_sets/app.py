from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.toml",
    environments=True,
    # merge_enabled=True  # this enabled global merge of all files
)

print(settings.A)

assert settings.get("A").get("B").get("C") == "1"
assert settings.get("A").get("cousin").get("D") == "2"
