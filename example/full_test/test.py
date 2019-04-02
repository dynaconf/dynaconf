from dynaconf import settings

# test default loader never gets cleaned

EXPECTED = {
    'ROOT_PATH_FOR_DYNACONF': '.',
    'ENV_FOR_DYNACONF': 'DEVELOPMENT',
    'DEFAULT_ENV_FOR_DYNACONF': 'DEFAULT',
    'GLOBAL_ENV_FOR_DYNACONF': 'DYNACONF',
    'ENCODING_FOR_DYNACONF': 'utf-8',
    'MERGE_ENABLED_FOR_DYNACONF': False,
    'ENVVAR_FOR_DYNACONF': 'SETTINGS_MODULE_FOR_DYNACONF',
    'REDIS_FOR_DYNACONF': {},
    'REDIS_ENABLED_FOR_DYNACONF': False,
    'VAULT_FOR_DYNACONF': {
        'url': 'http://localhost:8200',
        'token': None,
        'cert': None,
        'verify': None,
        'timeout': None,
        'proxies': None,
        'allow_redirects': None,
        'session': None
    },
    'VAULT_ENABLED_FOR_DYNACONF': False,
    'VAULT_PATH_FOR_DYNACONF': '/secret/data/',
    'CORE_LOADERS_FOR_DYNACONF': ['YAML', 'TOML', 'INI', 'JSON', 'PY'],
    'LOADERS_FOR_DYNACONF': ['dynaconf.loaders.env_loader'],
    'SILENT_ERRORS_FOR_DYNACONF': True,
    'FRESH_VARS_FOR_DYNACONF': [],
    'DEBUG_LEVEL_FOR_DYNACONF': 'DEBUG',
    'YAML': None,
    'TOML': None,
    'JSON': None,
    'INI': None,
    'DOTENV_PATH_FOR_DYNACONF': None,
    'DOTENV_VERBOSE_FOR_DYNACONF': False,
    'DOTENV_OVERRIDE_FOR_DYNACONF': False,
    'INSTANCE_FOR_DYNACONF': None,
    'YAML_LOADER_FOR_DYNACONF': 'full_load',
    'COMMENTJSON_ENABLED_FOR_DYNACONF': False,
    'SECRETS_FOR_DYNACONF': None,
    'INCLUDES_FOR_DYNACONF': [],
    'PYVAR': 'Come from settings.py',
    'TOMLVAR': 'come from toml',
    'YAMLVAR': 'Come from YAML',
    'INIVAR': 'come from ini',
    'JSONVAR': 'come from json'
}

for k, v in EXPECTED.items():
    current = settings.get(k)
    assert current == v, '{0} is {1} expected {2}'.format(k, current, v)

print("store:", settings.store)
print("loaders:", settings.loaded_by_loaders)
print("dotenv_overrride:", settings.DOTENV_OVERRIDE_FOR_DYNACONF)
print("redis:", settings.REDIS_FOR_DYNACONF)
print("PYVAR", settings.PYVAR)
print("YAMLVAR", settings.YAMLVAR)
print("TOMLVAR", settings.TOMLVAR)
print("INIVAR", settings.INIVAR)
print("JSONVAR", settings.JSONVAR)

print("cleaning.....")
settings.clean()
settings.execute_loaders()

print("store:", settings.store)
print("loaders:", settings.loaded_by_loaders)
print("deleted:", settings._deleted)
print("dotenv_override:", settings.DOTENV_OVERRIDE_FOR_DYNACONF)
print("redis:", settings.REDIS_FOR_DYNACONF)

print("PYVAR", settings.PYVAR)
print("YAMLVAR", settings.YAMLVAR)
print("TOMLVAR", settings.TOMLVAR)
print("INIVAR", settings.INIVAR)
print("JSONVAR", settings.JSONVAR)

with settings.using_env('staging'):
    print("PYVAR", settings.PYVAR)
    print("YAMLVAR", settings.YAMLVAR)
    print("TOMLVAR", settings.TOMLVAR)
    print("INIVAR", settings.INIVAR)
    print("JSONVAR", settings.JSONVAR)

print("store:", settings.store)
print("loaders:", settings.loaded_by_loaders)
print("deleted:", settings._deleted)
print("dotenv_override:", settings.DOTENV_OVERRIDE_FOR_DYNACONF)
print("redis:", settings.REDIS_FOR_DYNACONF)
print("PYVAR", settings.PYVAR)
print("YAMLVAR", settings.YAMLVAR)
print("TOMLVAR", settings.TOMLVAR)
print("INIVAR", settings.INIVAR)
print("JSONVAR", settings.JSONVAR)


settings.setenv('staging')
print("PYVAR", settings.PYVAR)
print("YAMLVAR", settings.YAMLVAR)
print("TOMLVAR", settings.TOMLVAR)
print("INIVAR", settings.INIVAR)
print("JSONVAR", settings.JSONVAR)
print("store:", settings.store)
print("loaders:", settings.loaded_by_loaders)
print("deleted:", settings._deleted)
print("dotenv_override:", settings.DOTENV_OVERRIDE_FOR_DYNACONF)
print("redis:", settings.REDIS_FOR_DYNACONF)

settings.setenv()
print("PYVAR", settings.PYVAR)
print("YAMLVAR", settings.YAMLVAR)
print("TOMLVAR", settings.TOMLVAR)
print("INIVAR", settings.INIVAR)
print("JSONVAR", settings.JSONVAR)
print("store:", settings.store)
print("loaders:", settings.loaded_by_loaders)
print("deleted:", settings._deleted)
print("dotenv_override:", settings.DOTENV_OVERRIDE_FOR_DYNACONF)
print("redis:", settings.REDIS_FOR_DYNACONF)
