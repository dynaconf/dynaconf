from dynaconf import settings

# test default loader never gets cleaned

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

with settings.using_env('dev'):
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


settings.setenv('dev')
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


