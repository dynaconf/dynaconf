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
# HERE STARTS DYNACONF EXTENSION LOAD
# Important! Keep it at the very bottom of your Django's settings.py file
# Read more at https://dynaconf.readthedocs.io/en/latest/guides/django.html
# Tip: All the variables defined above can now be moved to
# `../settings.toml` under `[default]` section.
import os, sys, dynaconf  # noqa
dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
dynaconf.default_settings.start_dotenv(root_path=os.path.dirname(os.path.abspath(__file__)))  # noqa
settings = dynaconf.DjangoDynaconf(sys.modules[__name__])  # noqa
# Important! No more code below this line
# HERE ENDS DYNACONF EXTENSION LOAD
 '''
