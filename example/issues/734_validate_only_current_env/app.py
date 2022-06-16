from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import ValidationError
from dynaconf import Validator

settings_dev = Dynaconf(
    settings_files=["settings.toml"],
    environments=True,
    force_env="development",
)

settings_prod = Dynaconf(
    settings_files=["settings.toml"], environments=True, force_env="production"
)

settings_dev.validators.register(
    Validator("API_KEY", env="production", must_exist=True)
)

settings_prod.validators.register(
    Validator("API_KEY", env="production", must_exist=True)
)

# Will not fail event if production env has no API_KEY
settings_dev.validators.validate(only_current_env=True)

# Will fail as production env has no API_KEY and current env is production
try:
    settings_prod.validators.validate(only_current_env=True)
except ValidationError as e:
    print(e)
