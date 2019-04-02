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
import os  # noqa
import sys  # noqa
import dynaconf  # noqa
_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
dynaconf.default_settings.start_dotenv(root_path=_ROOT_PATH)

# For a list of config keys see:
# https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
# Those keys can also be set as environment variables.
lazy_settings = dynaconf.LazySettings(
    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='DJANGO',
    ENV_FOR_DYNACONF=os.environ.get('DJANGO_ENV', 'DEVELOPMENT'),
    ROOT_PATH_FOR_DYNACONF=_ROOT_PATH,
    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}
)

# This makes django check happy because all settings is provided
for setting_name, setting_value in lazy_settings._store.items():
    setattr(sys.modules[__name__], setting_name.upper(), setting_value)

# This import makes `django.conf.settings` to behave dynamically
from dynaconf.contrib import django_dynaconf_v2  # noqa
django_dynaconf_v2.load(lazy_settings)
# HERE ENDS DYNACONF PATCHING
 '''
