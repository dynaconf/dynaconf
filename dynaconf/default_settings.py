# default proj root
# pragma: no cover
PROJECT_ROOT_FOR_DYNACONF = "."

# Default settings file
SETTINGS_MODULE_FOR_DYNACONF = (
    'settings.py,'
    'settings.yaml,settings.yml,'
    'settings.toml,settings.tml,'
    'settings.ini,settings.conf,settings.properties,'
    'settings.json'
)

# Namespace for envvars
NAMESPACE_FOR_DYNACONF = 'DYNACONF'

# The env var specifying settings module
ENVVAR_FOR_DYNACONF = "DYNACONF_SETTINGS"

# Default values for redis configs
REDIS_FOR_DYNACONF = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

# Loaders to read namespace based vars from different data stores
LOADERS_FOR_DYNACONF = [
    'dynaconf.loaders.env_loader',
    # 'dynaconf.loaders.redis_loader'
]

# Errors in loaders should be silenced?
SILENT_ERRORS_FOR_DYNACONF = False

# always fresh variables
FRESH_VARS_FOR_DYNACONF = []

# debug
DEBUG_LEVEL_FOR_DYNACONF = 'ERROR'

YAML = None
TOML = None
JSON = None
INI = None

DOTENV_PATH_FOR_DYNACONF = None
DOTENV_VERBOSE_FOR_DYNACONF = False
DOTENV_OVERRIDE_FOR_DYNACONF = False
