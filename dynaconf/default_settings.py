import importlib
import os
import sys
import warnings

from dynaconf.utils import raw_logger
from dynaconf.utils import RENAMED_VARS
from dynaconf.utils import upperfy
from dynaconf.utils import warn_deprecations
from dynaconf.utils.files import find_file
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda *args, **kwargs: None  # noqa


def try_renamed(key, value, older_key, current_key):
    if value is None:
        if key == current_key:
            if older_key in os.environ:
                warnings.warn(
                    "{0} is deprecated please use {1}".format(
                        older_key, current_key
                    ),
                    DeprecationWarning,
                )
                value = os.environ[older_key]
    return value


def get(key, default=None):
    value = os.environ.get(upperfy(key))

    # compatibility with renamed variables
    for old, new in RENAMED_VARS.items():
        value = try_renamed(key, value, old, new)

    return (
        parse_conf_data(value, tomlfy=True) if value is not None else default
    )


def start_dotenv(obj=None, root_path=None):
    # load_from_dotenv_if_installed
    obj = obj or {}
    _find_file = getattr(obj, "find_file", find_file)
    root_path = (
        root_path
        or getattr(obj, "_root_path", None)
        or get("ROOT_PATH_FOR_DYNACONF")
    )
    raw_logger().debug(
        "Starting Dynaconf Dotenv %s",
        "for {0}".format(root_path) if root_path else "Base",
    )

    dotenv_path = (
        obj.get("DOTENV_PATH_FOR_DYNACONF")
        or get("DOTENV_PATH_FOR_DYNACONF")
        or _find_file(".env", project_root=root_path)
    )

    load_dotenv(
        dotenv_path,
        verbose=obj.get("DOTENV_VERBOSE_FOR_DYNACONF", False),
        override=obj.get("DOTENV_OVERRIDE_FOR_DYNACONF", False),
    )

    warn_deprecations(os.environ)


def reload(*args, **kwargs):
    start_dotenv(*args, **kwargs)
    importlib.reload(sys.modules[__name__])


# default proj root
# pragma: no cover
ROOT_PATH_FOR_DYNACONF = get("ROOT_PATH_FOR_DYNACONF", None)

# Default settings file
default_paths = (
    "settings.py,.secrets.py,"
    "settings.toml,settings.tml,.secrets.toml,.secrets.tml,"
    "settings.yaml,settings.yml,.secrets.yaml,.secrets.yml,"
    "settings.ini,settings.conf,settings.properties,"
    ".secrets.ini,.secrets.conf,.secrets.properties,"
    "settings.json,.secrets.json"
)
SETTINGS_FILE_FOR_DYNACONF = get("SETTINGS_FILE_FOR_DYNACONF", default_paths)

# # ENV SETTINGS
# # In dynaconf 1.0.0 `NAMESPACE` got renamed to `ENV`

# The environment variable to switch current env
ENV_SWITCHER_FOR_DYNACONF = get(
    "ENV_SWITCHER_FOR_DYNACONF", "ENV_FOR_DYNACONF"
)

# The current env by default is DEVELOPMENT
# to switch is needed to `export ENV_FOR_DYNACONF=PRODUCTION`
# or put that value in .env file
# this value is used only when reading files like .toml|yaml|ini|json
ENV_FOR_DYNACONF = get(ENV_SWITCHER_FOR_DYNACONF, "DEVELOPMENT")

# This variable exists to support `from_env` method
FORCE_ENV_FOR_DYNACONF = get("FORCE_ENV_FOR_DYNACONF", None)

# Default values is taken from DEFAULT pseudo env
# this value is used only when reading files like .toml|yaml|ini|json
DEFAULT_ENV_FOR_DYNACONF = get("DEFAULT_ENV_FOR_DYNACONF", "DEFAULT")

# Global values are taken from DYNACONF env used for exported envvars
# Values here overwrites all other envs
# This namespace is used for files and also envvars
ENVVAR_PREFIX_FOR_DYNACONF = get("ENVVAR_PREFIX_FOR_DYNACONF", "DYNACONF")

# The default encoding to open settings files
ENCODING_FOR_DYNACONF = get("ENCODING_FOR_DYNACONF", "utf-8")

# Merge objects on load
MERGE_ENABLED_FOR_DYNACONF = get("MERGE_ENABLED_FOR_DYNACONF", False)

# BY default `__` is the separator for nested env vars
# export `DYNACONF__DATABASE__server=server.com`
# export `DYNACONF__DATABASE__PORT=6666`
# Should result in settings.DATABASE == {'server': 'server.com', 'PORT': 6666}
# To disable it one can set `NESTED_SEPARATOR_FOR_DYNACONF=false`
NESTED_SEPARATOR_FOR_DYNACONF = get("NESTED_SEPARATOR_FOR_DYNACONF", "__")

# The env var specifying settings module
ENVVAR_FOR_DYNACONF = get("ENVVAR_FOR_DYNACONF", "SETTINGS_FILE_FOR_DYNACONF")

# Default values for redis configs
default_redis = {
    "host": get("REDIS_HOST_FOR_DYNACONF", "localhost"),
    "port": int(get("REDIS_PORT_FOR_DYNACONF", 6379)),
    "db": int(get("REDIS_DB_FOR_DYNACONF", 0)),
    "decode_responses": get("REDIS_DECODE_FOR_DYNACONF", True),
}
REDIS_FOR_DYNACONF = get("REDIS_FOR_DYNACONF", default_redis)
REDIS_ENABLED_FOR_DYNACONF = get("REDIS_ENABLED_FOR_DYNACONF", False)

# Hashicorp Vault Project
vault_scheme = get("VAULT_SCHEME_FOR_DYNACONF", "http")
vault_host = get("VAULT_HOST_FOR_DYNACONF", "localhost")
vault_port = get("VAULT_PORT_FOR_DYNACONF", "8200")
default_vault = {
    "url": get(
        "VAULT_URL_FOR_DYNACONF",
        "{}://{}:{}".format(vault_scheme, vault_host, vault_port),
    ),
    "token": get("VAULT_TOKEN_FOR_DYNACONF", None),
    "cert": get("VAULT_CERT_FOR_DYNACONF", None),
    "verify": get("VAULT_VERIFY_FOR_DYNACONF", None),
    "timeout": get("VAULT_TIMEOUT_FOR_DYNACONF", None),
    "proxies": get("VAULT_PROXIES_FOR_DYNACONF", None),
    "allow_redirects": get("VAULT_ALLOW_REDIRECTS_FOR_DYNACONF", None),
}
VAULT_FOR_DYNACONF = get("VAULT_FOR_DYNACONF", default_vault)
VAULT_ENABLED_FOR_DYNACONF = get("VAULT_ENABLED_FOR_DYNACONF", False)
VAULT_PATH_FOR_DYNACONF = get("VAULT_PATH_FOR_DYNACONF", "dynaconf")
VAULT_ROLE_ID_FOR_DYNACONF = get("VAULT_ROLE_ID_FOR_DYNACONF", None)
VAULT_SECRET_ID_FOR_DYNACONF = get("VAULT_SECRET_ID_FOR_DYNACONF", None)

# Only core loaders defined on this list will be invoked
core_loaders = ["YAML", "TOML", "INI", "JSON", "PY"]
CORE_LOADERS_FOR_DYNACONF = get("CORE_LOADERS_FOR_DYNACONF", core_loaders)

# External Loaders to read vars from different data stores
default_loaders = [
    "dynaconf.loaders.env_loader",
    # 'dynaconf.loaders.redis_loader'
    # 'dynaconf.loaders.vault_loader'
]
LOADERS_FOR_DYNACONF = get("LOADERS_FOR_DYNACONF", default_loaders)

# Errors in loaders should be silenced?
SILENT_ERRORS_FOR_DYNACONF = get("SILENT_ERRORS_FOR_DYNACONF", True)

# always fresh variables
FRESH_VARS_FOR_DYNACONF = get("FRESH_VARS_FOR_DYNACONF", [])

# debug
DEBUG_LEVEL_FOR_DYNACONF = get("DEBUG_LEVEL_FOR_DYNACONF", "NOTSET")

DOTENV_PATH_FOR_DYNACONF = get("DOTENV_PATH_FOR_DYNACONF", None)
DOTENV_VERBOSE_FOR_DYNACONF = get("DOTENV_VERBOSE_FOR_DYNACONF", False)
DOTENV_OVERRIDE_FOR_DYNACONF = get("DOTENV_OVERRIDE_FOR_DYNACONF", False)

# Currently this is only used by cli. INSTANCE_FOR_DYNACONF specifies python
# dotted path to custom LazySettings instance. Last dotted path item should be
# instance of LazySettings.
INSTANCE_FOR_DYNACONF = get("INSTANCE_FOR_DYNACONF", None)

# https://msg.pyyaml.org/load
YAML_LOADER_FOR_DYNACONF = get("YAML_LOADER_FOR_DYNACONF", "full_load")

# Use commentjson? https://commentjson.readthedocs.io/en/latest/
COMMENTJSON_ENABLED_FOR_DYNACONF = get(
    "COMMENTJSON_ENABLED_FOR_DYNACONF", False
)

# Extra file, or list of files where to look for secrets
# useful for CI environment like jenkins
# where you can export this variable pointing to a local
# absolute path of the secrets file.
SECRETS_FOR_DYNACONF = get("SECRETS_FOR_DYNACONF", None)

# To include extra paths based on envvar
INCLUDES_FOR_DYNACONF = get("INCLUDES_FOR_DYNACONF", [])

# To pre-load extra paths based on envvar
PRELOAD_FOR_DYNACONF = get("PRELOAD_FOR_DYNACONF", [])

# Files to skip if found on search tree
SKIP_FILES_FOR_DYNACONF = get("SKIP_FILES_FOR_DYNACONF", [])


# Backwards compatibility with renamed variables
for old, new in RENAMED_VARS.items():
    setattr(sys.modules[__name__], old, locals()[new])
