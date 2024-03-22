from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    environments=["unit_testing", "dev_coding", "prod_server"],
)

unit_settings = settings.from_env("unit_testing")
dev_settings = settings.from_env("dev_coding")
prod_settings = settings.from_env("prod_server")

assert settings.name == "default"
assert unit_settings.name == "unit"
assert dev_settings.name == "dev"
assert prod_settings.name == "prod"

settings.setenv("prod_server")
assert settings.name == "prod"
