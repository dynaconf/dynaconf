import os
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda *args, **kwargs: None  # noqa
    find_dotenv = lambda: None  # noqa


def try_renamed(key, value, current_key, older_key):
    if value is None:
        if key == current_key:
            value = os.environ.get(older_key)
    return value


def get(key, default=None):
    value = os.environ.get(key.upper())

    # compatibility renames before 1.x version
    value = try_renamed(key, value, 'ENV_FOR_DYNACONF',
                        'NAMESPACE_FOR_DYNACONF')
    value = try_renamed(key, value, 'ENV_FOR_DYNACONF',
                        'DYNACONF_NAMESPACE')
    value = try_renamed(key, value, 'DEFAULT_ENV_FOR_DYNACONF',
                        'BASE_NAMESPACE_FOR_DYNACONF')
    value = try_renamed(key, value, 'SETTINGS_MODULE_FOR_DYNACONF',
                        'DYNACONF_SETTINGS')

    return parse_conf_data(
        value, tomlfy=True) if value is not None else default


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
    'settings.toml,settings.tml,.secrets.toml,.secrets.tml,'
    'settings.yaml,settings.yml,.secrets.yaml,.secrets.yml,'
    'settings.ini,settings.conf,settings.properties,'
    '.secrets.ini,.secrets.conf,.secrets.properties,'
    'settings.json,.secrets.json'
)
SETTINGS_MODULE_FOR_DYNACONF = get('SETTINGS_MODULE_FOR_DYNACONF',
                                   default_paths)

# # ENV SETTINGS
# # In dynaconf 1.0.0 `NAMESPACE` got renamed to `ENV`

# The current env by default is DEVELOPMENT
# to switch is needed to `export ENV_FOR_DYNACONF=PRODUCTION`
# or put that value in .env file
# this value is used only when reading files like .toml|yaml|ini|json
ENV_FOR_DYNACONF = get('ENV_FOR_DYNACONF', 'DEVELOPMENT')

# Default values is taken from DEFAULT pseudo env
# this value is used only when reading files like .toml|yaml|ini|json
DEFAULT_ENV_FOR_DYNACONF = get('DEFAULT_ENV_FOR_DYNACONF', 'DEFAULT')

# Global values are taken from DYNACONF env used for exported envvars
# Values here overwrites all other envs
# This namespace is used for files and also envvars
GLOBAL_ENV_FOR_DYNACONF = get('GLOBAL_ENV_FOR_DYNACONF', 'DYNACONF')

# The env var specifying settings module
ENVVAR_FOR_DYNACONF = get('ENVVAR_FOR_DYNACONF',
                          'SETTINGS_MODULE_FOR_DYNACONF')

# Default values for redis configs
default_redis = {
    'host': get('REDIS_HOST_FOR_DYNACONF', 'localhost'),
    'port': int(get('REDIS_PORT_FOR_DYNACONF', 6379)),
    'db': int(get('REDIS_DB_FOR_DYNACONF', 0)),
    'decode_responses': get('REDIS_DECODE_FOR_DYNACONF', True)
}
REDIS_FOR_DYNACONF = get('REDIS_FOR_DYNACONF', default_redis)
REDIS_ENABLED_FOR_DYNACONF = get('REDIS_ENABLED_FOR_DYNACONF', False)

# Hashicorp Vault Project
vault_scheme = get('VAULT_SCHEME_FOR_DYNACONF', 'http')
vault_host = get('VAULT_HOST_FOR_DYNACONF', 'localhost')
vault_port = get('VAULT_PORT_FOR_DYNACONF', '8200')
default_vault = {
    'url': get('VAULT_URL_FOR_DYNACONF', '{}://{}:{}'.format(
        vault_scheme, vault_host, vault_port)
    ),
    'token': get('VAULT_TOKEN_FOR_DYNACONF', None),
    'cert': get('VAULT_CERT_FOR_DYNACONF', None),
    'verify': get('VAULT_VERIFY_FOR_DYNACONF', None),
    'timeout': get('VAULT_TIMEOUT_FOR_DYNACONF', None),
    'proxies': get('VAULT_PROXIES_FOR_DYNACONF', None),
    'allow_redirects': get('VAULT_ALLOW_REDIRECTS_FOR_DYNACONF', None),
    'session': get('VAULT_SESSION_FOR_DYNACONF', None),
}
VAULT_FOR_DYNACONF = get('VAULT_FOR_DYNACONF', default_vault)
VAULT_ENABLED_FOR_DYNACONF = get('VAULT_ENABLED_FOR_DYNACONF', False)
VAULT_PATH_FOR_DYNACONF = get('VAULT_PATH_FOR_DYNACONF',
                              '/secret/data/')  # /DYNACONF will be added

# Loaders to read env based vars from different data stores
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
