from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf import Validator

# Load config files
config = Dynaconf(settings_files=["settings.toml"])


validators = [
    Validator(
        "version",
        is_type_of=str,
        default="0.30",  # this must not be transformed to float
        apply_default_on_none=True,
    ),
]

config.validators.register(*validators)
config.validators.validate()


print(type(config.version))
print(config.version)


assert config.version == "0.30"
assert isinstance(config.version, str)
