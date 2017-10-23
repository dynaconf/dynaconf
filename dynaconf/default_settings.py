# default proj root
# pragma: no cover
from os import path

PROJECT_ROOT = "."

_found_config_files = [
    f for f in ('settings.py', 'settings.yml', 'settings.yaml')
    if path.exists(path.join(PROJECT_ROOT, f))
]
if len(_found_config_files) == 0:
    _found_config_files.append('settings.py')


class MultipleConfigFilesError(Exception):
    pass


if len(_found_config_files) > 1:
    raise MultipleConfigFilesError(
        'Found multiple config files on root directory: {}. '
        'Only one settings file is allowed. '
        'So you can change change file names and use DYNACONF_SETTINGS '
        'env var to set the file you want to use'.format(
            '.'.join(_found_config_files))
    )

SETTINGS_MODULE_FOR_DYNACONF = _found_config_files[0]

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
