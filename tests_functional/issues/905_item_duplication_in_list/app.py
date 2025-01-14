from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml"],
    environments=True,
    load_dotenv=True,
    merge_enabled=True,
)


settings.validators.register(
    Validator("group.something_new", default=5),
)

settings.validators.validate()

assert settings.group.test_list == ["1", "2"], settings.group.test_list
assert settings.group.something_new == 5
assert settings.group.another_setting == "ciao"
assert settings.group.another == 45
