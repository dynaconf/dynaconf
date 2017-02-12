# default proj root
# pragma: no cover
PROJECT_ROOT = "."

# Default settings file
SETTINGS_MODULE_FOR_DYNACONF = 'settings.py'

# Namespace for envvars
DYNACONF_NAMESPACE = 'DYNACONF'

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
DYNACONF_SILENT_ERRORS = False

# always fresh variables
DYNACONF_ALWAYS_FRESH_VARS = []
