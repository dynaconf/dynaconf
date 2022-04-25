from dynaconf import LazySettings
from dynaconf import Validator

settings = LazySettings(
    envvar_prefix="TESTING",
    core_loaders=["YAML"],
    settings_file="settings.yaml",
    preload=["*.yaml"],
    envless_mode=True,
    lowercase_rad=True,
)

validators = dict(
    nested=[
        Validator("nested.test_field", default=None),
        (
            Validator("nested.group_field", must_exist=True)
            | Validator("nested.group_field_two", must_exist=True)
        ),
    ],
)

settings.validators.register(**validators)
settings.validators.validate()
