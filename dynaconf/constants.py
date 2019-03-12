# pragma: no cover
INI_EXTENSIONS = ('.ini', '.conf', '.properties',)
TOML_EXTENSIONS = ('.toml', '.tml',)
YAML_EXTENSIONS = ('.yaml', '.yml',)
JSON_EXTENSIONS = ('.json',)

ALL_EXTENSIONS = INI_EXTENSIONS + TOML_EXTENSIONS + YAML_EXTENSIONS + JSON_EXTENSIONS  # noqa

EXTERNAL_LOADERS = {
    'ENV': 'dynaconf.loaders.env_loader',
    'REDIS': 'dynaconf.loaders.redis_loader',
    'VAULT': 'dynaconf.loaders.vault_loader',
}

DJANGO_PATCH = '''

# HERE STARTS DYNACONF PATCHING

import os # noqa
import sys  # noqa
from dynaconf import LazySettings  # noqa

# For a list of config keys see:
# https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
# Those keys can also be set as environment variables.
lazy_settings = LazySettings(
    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='DJANGO',
    ENV_FOR_DYNACONF=os.environ.get('DJANGO_ENV', 'DEVELOPMENT'),
    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}
)


def __getattr__(name):  # noqa
    """This function will be used by Python 3.7+"""
    return getattr(lazy_settings, name)


def __dir__():  # noqa
    """This function will be used by Python 3.7+"""
    return dir(lazy_settings)


for setting_name, setting_value in lazy_settings._store.items():
    setattr(sys.modules[__name__], setting_name.upper(), setting_value)

# This import makes `django.conf.settings` to behave dynamically
import dynaconf.contrib.django_dynaconf # noqa

# HERE ENDS DYNACONF PATCHING

'''
