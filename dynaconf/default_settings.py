import os
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda *args, **kwargs: None  # noqa
    find_dotenv = lambda: None  # noqa


def get(key, default=None):
    return parse_conf_data(os.environ.get(key.upper(), default))


def start_dotenv(obj=None):
    # load_from_dotenv_if_installed
    obj = obj or {}
    dotenv_path = obj.get('DOTENV_PATH_FOR_DYNACONF') or os.environ.get(
        'DOTENV_PATH_FOR_DYNACONF') or find_dotenv(usecwd=True)
    load_dotenv(
        dotenv_path,
        verbose=obj.get('DOTENV_VERBOSE_FOR_DYNACONF', False),
        override=obj.get('DOTENV_OVERRIDE_FOR_DYNACONF', False)
    )


start_dotenv()


# default proj root
# pragma: no cover
PROJECT_ROOT_FOR_DYNACONF = get('PROJECT_ROOT_FOR_DYNACONF', ".")

# Default settings file
default_paths = (
    'settings.py,.secrets.py,'
    'settings.yaml,settings.yml,.secrets.yaml,.secrets.yml,'
    'settings.toml,settings.tml,.secrets.toml,.secrets.tml,'
    'settings.ini,settings.conf,settings.properties,'
    '.secrets.ini,.secrets.conf,.secrets.properties,'
    'settings.json,.secrets.json'
)
SETTINGS_MODULE_FOR_DYNACONF = get('SETTINGS_MODULE_FOR_DYNACONF',
                                   default_paths)

# Namespace for envvars
NAMESPACE_FOR_DYNACONF = get('NAMESPACE_FOR_DYNACONF', 'DYNACONF')
BASE_NAMESPACE_FOR_DYNACONF = get('BASE_NAMESPACE_FOR_DYNACONF', 'DYNACONF')

# The env var specifying settings module
ENVVAR_FOR_DYNACONF = get('ENVVAR_FOR_DYNACONF', 'DYNACONF_SETTINGS')

# Default values for redis configs
default_redis = {
    'host': get('REDIS_FOR_DYNACONF_HOST', 'localhost'),
    'port': int(get('REDIS_FOR_DYNACONF_PORT', 6379)),
    'db': int(get('REDIS_FOR_DYNACONF_DB', 0)),
    'decode_responses': True
}
REDIS_FOR_DYNACONF = get('REDIS_FOR_DYNACONF', default_redis)
REDIS_FOR_DYNACONF_ENABLED = get('REDIS_FOR_DYNACONF_ENABLED', False)

# Hashicorp Vault Project
vault_scheme = get('VAULT_FOR_DYNACONF_SCHEME', 'http')
vault_url = get('VAULT_FOR_DYNACONF_HOST', 'localhost')
vault_port = get('VAULT_FOR_DYNACONF_PORT', '8200')
default_vault = {
    'url': get('VAULT_FOR_DYNACONF_URL', '{}://{}:{}'.format(
        vault_scheme, vault_url, vault_port)
    ),
    'token': get('VAULT_FOR_DYNACONF_TOKEN', None),
    'cert': get('VAULT_FOR_DYNACONF_CERT', None),
    'verify': get('VAULT_FOR_DYNACONF_VERIFY', None),
    'timeout': get('VAULT_FOR_DYNACONF_TIMEOUT', None),
    'proxies': get('VAULT_FOR_DYNACONF_PROXIES', None),
    'allow_redirects': get('VAULT_FOR_DYNACONF_ALLOW_REDIRECTS', None),
    'session': get('VAULT_FOR_DYNACONF_SESSION', None),
}
VAULT_FOR_DYNACONF = get('VAULT_FOR_DYNACONF', default_vault)
VAULT_FOR_DYNACONF_ENABLED = get('VAULT_FOR_DYNACONF_ENABLED', False)
VAULT_FOR_DYNACONF_PATH = get('VAULT_FOR_DYNACONF_PATH',
                              '/secret/data/')  # /namespace will be added

# Loaders to read namespace based vars from different data stores
default_loaders = [
    'dynaconf.loaders.env_loader',
    # 'dynaconf.loaders.redis_loader'
    # 'dynaconf.loaders.vault_loader'
]
LOADERS_FOR_DYNACONF = get('LOADERS_FOR_DYNACONF', default_loaders)

# Errors in loaders should be silenced?
SILENT_ERRORS_FOR_DYNACONF = get('SILENT_ERRORS_FOR_DYNACONF', True)

# always fresh variables
FRESH_VARS_FOR_DYNACONF = get('FRESH_VARS_FOR_DYNACONF', [])

# debug
DEBUG_LEVEL_FOR_DYNACONF = get('DEBUG_LEVEL_FOR_DYNACONF', 'NOTSET')

YAML = get('YAML', None)
TOML = get('TOML', None)
JSON = get('JSON', None)
INI = get('INI', None)

DOTENV_PATH_FOR_DYNACONF = get('DOTENV_PATH_FOR_DYNACONF', None)
DOTENV_VERBOSE_FOR_DYNACONF = get('DOTENV_VERBOSE_FOR_DYNACONF', False)
DOTENV_OVERRIDE_FOR_DYNACONF = get('DOTENV_OVERRIDE_FOR_DYNACONF', False)
