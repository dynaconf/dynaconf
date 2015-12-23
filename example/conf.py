# coding: utf-8
from dynaconf import LazySettings

settings = LazySettings(
    ENVVAR_FOR_DYNACONF="EXAMPLE_SETTINGS_MODULE",
    DYNACONF_NAMESPACE='EXAMPLE',
)
